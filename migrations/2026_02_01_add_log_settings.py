"""
Migration: Add log rotation settings

This migration adds default settings for log file rotation management.

Settings Added:
- log_max_size_mb: Maximum size of log file in MB before rotation (default: 10)
- log_backup_count: Number of rotated log files to keep (default: 5)

Purpose:
Allows administrators to configure how error logs are rotated to prevent
disk space issues while maintaining historical error data for troubleshooting.
"""

MIGRATION_ID = "2026_02_01_add_log_settings"

def upgrade(conn, column_exists, table_exists):
    """Add default log rotation settings"""
    cursor = conn.cursor()

    # Create settings table if it doesn't exist
    if not table_exists('settings'):
        cursor.execute("""
            CREATE TABLE settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                description TEXT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key)")
        print("  ✓ Created settings table")

    # Check if settings already exist
    cursor.execute("SELECT key FROM settings WHERE key IN ('log_max_size_mb', 'log_backup_count')")
    existing_settings = {row[0] for row in cursor.fetchall()}

    if 'log_max_size_mb' not in existing_settings:
        cursor.execute("""
            INSERT INTO settings (key, value, description)
            VALUES ('log_max_size_mb', '10', 'Maximum size of log file in MB before rotation')
        """)
        print("  ✓ Added log_max_size_mb setting")
    else:
        print("  ℹ️  log_max_size_mb setting already exists, skipping")

    if 'log_backup_count' not in existing_settings:
        cursor.execute("""
            INSERT INTO settings (key, value, description)
            VALUES ('log_backup_count', '5', 'Number of rotated log files to keep')
        """)
        print("  ✓ Added log_backup_count setting")
    else:
        print("  ℹ️  log_backup_count setting already exists, skipping")
