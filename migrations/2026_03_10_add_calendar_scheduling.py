"""
Add calendar-based scheduling support to employee position schedules.

This migration adds the ability to schedule employees on specific calendar dates
in addition to the existing recurring days-of-week scheduling.

Changes:
- Adds 'schedule_type' column to employee_position_schedule table
  Values: 'recurring' (default) or 'calendar'
- Adds 'specific_dates' JSON column to store array of date strings
  Format: ["2026-03-15", "2026-03-22", ...]

This allows employees to be scheduled either:
1. Recurring weekly (existing behavior): ["Monday", "Wednesday", "Friday"]
2. Specific dates (new): ["2026-03-15", "2026-03-22", "2026-03-29"]

The daily balance auto-population will check both schedule types:
- For 'recurring': Match day_of_week in days_of_week array
- For 'calendar': Match target date in specific_dates array

Note: Existing schedules are preserved and default to 'recurring' type.
"""

MIGRATION_ID = "2026_03_10_add_calendar_scheduling"


def upgrade(conn, column_exists, table_exists):
    """
    Apply the migration.

    Args:
        conn: SQLite database connection
        column_exists: Helper - column_exists(table, column) -> bool
        table_exists: Helper - table_exists(table) -> bool
    """
    cursor = conn.cursor()

    # Add schedule_type column
    if not column_exists('employee_position_schedule', 'schedule_type'):
        cursor.execute("""
            ALTER TABLE employee_position_schedule
            ADD COLUMN schedule_type TEXT DEFAULT 'recurring'
        """)
        print("  ✓ Added schedule_type column to employee_position_schedule")

        # Set all existing schedules to 'recurring' type
        cursor.execute("""
            UPDATE employee_position_schedule
            SET schedule_type = 'recurring'
            WHERE schedule_type IS NULL
        """)
        print("  ✓ Set existing schedules to 'recurring' type")
    else:
        print("  ℹ️  schedule_type column already exists, skipping")

    # Add specific_dates column
    if not column_exists('employee_position_schedule', 'specific_dates'):
        cursor.execute("""
            ALTER TABLE employee_position_schedule
            ADD COLUMN specific_dates TEXT DEFAULT '[]'
        """)
        print("  ✓ Added specific_dates column to employee_position_schedule")

        # Initialize as empty array for existing records
        cursor.execute("""
            UPDATE employee_position_schedule
            SET specific_dates = '[]'
            WHERE specific_dates IS NULL OR specific_dates = ''
        """)
        print("  ✓ Initialized specific_dates as empty arrays")
    else:
        print("  ℹ️  specific_dates column already exists, skipping")

    conn.commit()
    print("  ✅ Calendar scheduling migration completed successfully")
