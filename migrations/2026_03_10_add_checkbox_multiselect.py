"""
Add checkbox multi-select functionality for tip requirements on daily employee entries.

This migration adds the ability to select multiple checkboxes for each employee
in the daily balance form, which can be used for tracking various requirements,
statuses, or attributes beyond just tip values.

Changes:
- Adds 'selected_checkboxes' JSON column to daily_employee_entries table
  Format: ["checkbox_slug_1", "checkbox_slug_2", ...]

This allows for flexible multi-select tracking of:
- Attendance markers
- Shift types
- Special conditions
- Custom attributes defined by TipEntryRequirement.record_data flag

The checkboxes are stored as an array of field_name slugs from tip_entry_requirements
where record_data=true.

Note: This is separate from tip_values (which stores numeric data) and provides
a way to capture boolean/selection data per employee per day.
"""

MIGRATION_ID = "2026_03_10_add_checkbox_multiselect"


def upgrade(conn, column_exists, table_exists):
    """
    Apply the migration.

    Args:
        conn: SQLite database connection
        column_exists: Helper - column_exists(table, column) -> bool
        table_exists: Helper - table_exists(table) -> bool
    """
    cursor = conn.cursor()

    # Add selected_checkboxes column
    if not column_exists('daily_employee_entries', 'selected_checkboxes'):
        cursor.execute("""
            ALTER TABLE daily_employee_entries
            ADD COLUMN selected_checkboxes TEXT DEFAULT '[]'
        """)
        print("  ✓ Added selected_checkboxes column to daily_employee_entries")

        # Initialize as empty array for existing records
        cursor.execute("""
            UPDATE daily_employee_entries
            SET selected_checkboxes = '[]'
            WHERE selected_checkboxes IS NULL OR selected_checkboxes = ''
        """)
        print("  ✓ Initialized selected_checkboxes as empty arrays for existing entries")
    else:
        print("  ℹ️  selected_checkboxes column already exists, skipping")

    conn.commit()
    print("  ✅ Checkbox multi-select migration completed successfully")
