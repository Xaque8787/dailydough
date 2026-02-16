"""
Add report metadata tracking fields

This migration adds comprehensive report metadata tracking to the daily_balance table.
Tracks both the user who generated the report (on first save) and who finalized it.

Changes:
- Add generated_by_user_id column to track who created the report
- Add generated_at column to track when the report was first created
- Add edited_at column to track when the report was last edited
- Add finalized_by_user_id column to track who finalized the report

Notes:
- Both generated_by and finalized_by will always be shown in reports for consistency
- edited_at only tracks the LAST edit time, not a full audit log
- For existing records, we'll populate generated_by from created_by_user_id if available
- This provides a complete audit trail of report creation, editing, and finalization
"""

MIGRATION_ID = "2026_02_16_add_report_metadata_fields"

def upgrade(conn, column_exists, table_exists):
    """Add report metadata tracking fields to daily_balance table."""
    cursor = conn.cursor()

    if not column_exists('daily_balance', 'generated_by_user_id'):
        cursor.execute("""
            ALTER TABLE daily_balance
            ADD COLUMN generated_by_user_id INTEGER
        """)
        print("  ✓ Added generated_by_user_id column to daily_balance table")
    else:
        print("  ℹ️  generated_by_user_id column already exists, skipping")

    if not column_exists('daily_balance', 'generated_at'):
        cursor.execute("""
            ALTER TABLE daily_balance
            ADD COLUMN generated_at TIMESTAMP
        """)
        print("  ✓ Added generated_at column to daily_balance table")
    else:
        print("  ℹ️  generated_at column already exists, skipping")

    if not column_exists('daily_balance', 'edited_at'):
        cursor.execute("""
            ALTER TABLE daily_balance
            ADD COLUMN edited_at TIMESTAMP
        """)
        print("  ✓ Added edited_at column to daily_balance table")
    else:
        print("  ℹ️  edited_at column already exists, skipping")

    if not column_exists('daily_balance', 'finalized_by_user_id'):
        cursor.execute("""
            ALTER TABLE daily_balance
            ADD COLUMN finalized_by_user_id INTEGER
        """)
        print("  ✓ Added finalized_by_user_id column to daily_balance table")
    else:
        print("  ℹ️  finalized_by_user_id column already exists, skipping")

    cursor.execute("""
        UPDATE daily_balance
        SET generated_by_user_id = created_by_user_id
        WHERE generated_by_user_id IS NULL
          AND created_by_user_id IS NOT NULL
    """)
    print("  ✓ Migrated existing created_by_user_id data to generated_by_user_id")

    cursor.execute("""
        UPDATE daily_balance
        SET finalized_by_user_id = COALESCE(edited_by_user_id, created_by_user_id)
        WHERE finalized = 1
          AND finalized_by_user_id IS NULL
    """)
    print("  ✓ Populated finalized_by_user_id for existing finalized reports")

    print("  ✓ Report metadata fields migration completed")
