"""
Denormalize Till Flags and Backfill Missing Starting Till Rows

Background:
  When a financial line item template flagged as is_starting_till or is_ending_till
  is deleted, SQLAlchemy's cascade="all, delete-orphan" on the template relationship
  deletes every historical daily_financial_line_items row that referenced it. This
  wipes the starting till values from all past finalized days.

Schema Changes:
  - daily_financial_line_items:
      + is_starting_till  BOOLEAN NOT NULL DEFAULT 0
      + is_ending_till    BOOLEAN NOT NULL DEFAULT 1

    These snapshot columns store the role of the line item at the time it was
    written, independent of whether the source template still exists.

  Backfill existing rows from current template data so the new columns are
  populated for all pre-existing rows that still have a live template reference.

Data Repair:
  For every finalized daily_balance day that is missing a row for the current
  is_starting_till template, insert one by chaining backward through the
  is_ending_till values:
    - Walk all finalized days chronologically
    - For each day missing a starting_till row, look up the ending_till value
      from the previous day
    - Insert a new daily_financial_line_items row linked to the current
      is_starting_till template, with that value and the snapshot flags set

  The chain walk ensures that even if multiple consecutive days are missing
  their starting till rows, each one is correctly reconstructed from the
  previous day's ending till (which may itself have been just repaired).

Notes:
  - Safe to run on a clean database: no missing rows = no-op for the backfill
  - Idempotent: skips days that already have a starting till row
  - Only inserts a row when exactly one is_starting_till template exists
"""

MIGRATION_ID = "2026_05_05_denormalize_till_flags_and_backfill"


def upgrade(conn, column_exists, table_exists):
    cursor = conn.cursor()

    # 1. Add is_starting_till snapshot column if missing
    if not column_exists("daily_financial_line_items", "is_starting_till"):
        cursor.execute("""
            ALTER TABLE daily_financial_line_items
            ADD COLUMN is_starting_till BOOLEAN NOT NULL DEFAULT 0
        """)
        print("  + Added is_starting_till column to daily_financial_line_items")
    else:
        print("  = is_starting_till column already exists, skipping")

    # 2. Add is_ending_till snapshot column if missing
    if not column_exists("daily_financial_line_items", "is_ending_till"):
        cursor.execute("""
            ALTER TABLE daily_financial_line_items
            ADD COLUMN is_ending_till BOOLEAN NOT NULL DEFAULT 0
        """)
        print("  + Added is_ending_till column to daily_financial_line_items")
    else:
        print("  = is_ending_till column already exists, skipping")

    # 3. Backfill snapshot flags for existing rows that still have a live template
    cursor.execute("""
        UPDATE daily_financial_line_items
        SET
            is_starting_till = COALESCE((
                SELECT t.is_starting_till
                FROM financial_line_item_templates t
                WHERE t.id = daily_financial_line_items.template_id
            ), 0),
            is_ending_till = COALESCE((
                SELECT t.is_ending_till
                FROM financial_line_item_templates t
                WHERE t.id = daily_financial_line_items.template_id
            ), 0)
        WHERE template_id IS NOT NULL
          AND is_employee_tip = 0
    """)
    backfilled_flags = cursor.rowcount
    print(f"  + Backfilled snapshot flags on {backfilled_flags} existing line item row(s)")

    # 4. Find the current is_starting_till template
    cursor.execute("""
        SELECT id, name, category, display_order
        FROM financial_line_item_templates
        WHERE is_starting_till = 1
    """)
    till_templates = cursor.fetchall()

    if not till_templates:
        print("  ! No is_starting_till template found — skipping starting till backfill")
        return

    if len(till_templates) > 1:
        print(f"  ! Multiple is_starting_till templates found ({len(till_templates)}) — "
              "skipping backfill to avoid ambiguity. Fix template configuration first.")
        return

    till_template_id, till_name, till_category, till_display_order = till_templates[0]
    print(f"  = Starting till template: id={till_template_id}, name='{till_name}'")

    # 5. Get all finalized days in chronological order
    cursor.execute("""
        SELECT id, date
        FROM daily_balance
        WHERE finalized = 1
        ORDER BY date ASC
    """)
    finalized_days = cursor.fetchall()

    if not finalized_days:
        print("  = No finalized days found — nothing to backfill")
        return

    print(f"  = Found {len(finalized_days)} finalized day(s) to check")

    inserted = 0
    skipped_has_row = 0
    skipped_no_prev = 0

    # Build a dict for fast lookup: date_str -> (balance_id, ending_till_value)
    # We'll populate ending_till values as we walk forward so repaired days
    # feed into the next day's starting till calculation.
    ending_till_by_date = {}

    # Pre-load existing ending till values for all finalized days
    cursor.execute("""
        SELECT db.date, dfli.value
        FROM daily_financial_line_items dfli
        JOIN daily_balance db ON db.id = dfli.daily_balance_id
        WHERE dfli.is_ending_till = 1
          AND db.finalized = 1
        ORDER BY db.date ASC
    """)
    for row_date, row_value in cursor.fetchall():
        ending_till_by_date[str(row_date)] = row_value

    from datetime import date as date_cls, timedelta

    for balance_id, balance_date in finalized_days:
        balance_date_str = str(balance_date)

        # Check if this day already has a starting till row
        cursor.execute("""
            SELECT id FROM daily_financial_line_items
            WHERE daily_balance_id = ?
              AND is_starting_till = 1
        """, (balance_id,))
        existing = cursor.fetchone()

        if existing:
            skipped_has_row += 1
            continue

        # No starting till row — find the previous day's ending till value
        if isinstance(balance_date, str):
            day_obj = date_cls.fromisoformat(balance_date)
        else:
            day_obj = balance_date

        prev_date_str = str(day_obj - timedelta(days=1))
        prev_ending_till = ending_till_by_date.get(prev_date_str, None)

        if prev_ending_till is None:
            # No previous day ending till available
            skipped_no_prev += 1
            print(f"  ~ Day {balance_date_str}: no previous ending till found "
                  f"(prev={prev_date_str}) — inserting 0.00 as starting till")
            prev_ending_till = 0.0

        # Determine the correct display_order: insert before the first non-till item
        # or use the template's display_order
        cursor.execute("""
            INSERT INTO daily_financial_line_items
                (daily_balance_id, template_id, name, category, value,
                 display_order, is_employee_tip, is_starting_till, is_ending_till)
            VALUES (?, ?, ?, ?, ?, ?, 0, 1, 0)
        """, (
            balance_id,
            till_template_id,
            till_name,
            till_category,
            prev_ending_till,
            till_display_order,
        ))
        inserted += 1
        print(f"  + Day {balance_date_str}: inserted starting till = {prev_ending_till:.2f}")

    print(f"  ✓ Backfill complete: {inserted} inserted, "
          f"{skipped_has_row} already had starting till row, "
          f"{skipped_no_prev} had no previous ending till (used 0.00)")
