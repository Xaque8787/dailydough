"""
Repair Orphaned Starting/Ending Till Template References

When a financial line item template flagged as is_starting_till or is_ending_till
is deleted and recreated (e.g., to fix a typo), historical DailyFinancialLineItem
rows are left with a template_id pointing to the now-deleted template. This causes
the previous-day ending till propagation to silently return 0 instead of the real value.

Changes:
- No schema changes

Data Repair:
- Finds all daily_financial_line_items rows whose template_id no longer exists in
  financial_line_item_templates (orphaned references)
- For each orphaned row, determines the role it should have (starting/ending till)
  by matching on the item's category and the is_starting_till / is_ending_till flags
  of existing templates
- Re-links the orphaned row to the correct current template if exactly one match exists
- Skips ambiguous cases (multiple matches) and logs them as warnings

Notes:
- This is a one-time data repair; it is safe to run on a clean database (no orphans = no-op)
- Only re-links rows where a single unambiguous replacement template can be found
- Does not touch rows that have no template_id (employee tip line items)
"""

MIGRATION_ID = "2026_05_05_repair_orphaned_till_template_references"


def upgrade(conn, column_exists, table_exists):
    cursor = conn.cursor()

    # Find all line item rows whose template_id points to a missing template
    cursor.execute("""
        SELECT dfli.id, dfli.template_id, dfli.category, dfli.name
        FROM daily_financial_line_items dfli
        LEFT JOIN financial_line_item_templates t ON t.id = dfli.template_id
        WHERE dfli.template_id IS NOT NULL
          AND t.id IS NULL
    """)
    orphaned_rows = cursor.fetchall()

    if not orphaned_rows:
        print("  ✓ No orphaned template references found, nothing to repair")
        return

    print(f"  Found {len(orphaned_rows)} orphaned line item row(s) to repair")

    repaired = 0
    skipped = 0

    for row_id, old_template_id, category, name in orphaned_rows:
        # Find candidate replacement templates: same category, is a till item
        cursor.execute("""
            SELECT id, name, is_starting_till, is_ending_till
            FROM financial_line_item_templates
            WHERE category = ?
              AND (is_starting_till = 1 OR is_ending_till = 1)
        """, (category,))
        candidates = cursor.fetchall()

        if not candidates:
            print(f"  ⚠ No replacement candidate found for orphaned row id={row_id} "
                  f"(old template_id={old_template_id}, category={category}, name='{name}') - skipping")
            skipped += 1
            continue

        if len(candidates) > 1:
            print(f"  ⚠ Multiple replacement candidates for orphaned row id={row_id} "
                  f"(old template_id={old_template_id}, category={category}, name='{name}') - skipping to avoid ambiguity")
            skipped += 1
            continue

        new_template_id, new_name, is_starting, is_ending = candidates[0]
        cursor.execute("""
            UPDATE daily_financial_line_items
            SET template_id = ?
            WHERE id = ?
        """, (new_template_id, row_id))
        print(f"  ✓ Repaired row id={row_id}: template_id {old_template_id} → {new_template_id} ('{new_name}')")
        repaired += 1

    print(f"  ✓ Repair complete: {repaired} repaired, {skipped} skipped")
