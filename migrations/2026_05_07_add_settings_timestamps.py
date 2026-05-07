"""
Migration: Add created_at and updated_at columns to settings table

The settings table was originally created without timestamp columns.
The SQLAlchemy model defines created_at and updated_at, so this migration
adds those columns to existing databases to prevent OperationalError on queries.

Changes:
  - settings: ADD COLUMN created_at TEXT (nullable)
  - settings: ADD COLUMN updated_at TEXT (nullable)
"""

MIGRATION_ID = "2026_05_07_add_settings_timestamps"


def upgrade(conn, column_exists, table_exists):
    if not table_exists("settings"):
        return

    if not column_exists("settings", "created_at"):
        conn.execute("ALTER TABLE settings ADD COLUMN created_at TEXT")
        print("  + settings.created_at added")

    if not column_exists("settings", "updated_at"):
        conn.execute("ALTER TABLE settings ADD COLUMN updated_at TEXT")
        print("  + settings.updated_at added")
