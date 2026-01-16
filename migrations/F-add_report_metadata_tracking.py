"""
Migration: Add Report Metadata Tracking

This migration adds metadata tracking to the DailyBalance table to record:
- Who created/finalized the report (user or scheduled task)
- When the report was finalized
- Who last edited the report

New columns:
- created_by_user_id: Foreign key to users table (NULL if created by scheduled task)
- created_by_source: 'user' or 'scheduled_task' to indicate the source
- edited_by_user_id: Foreign key to users table for tracking edits
- finalized_at: Timestamp of when the report was finalized
"""

import sqlite3
import os

# Detect environment: Docker vs bare-metal/IDE
if os.path.exists('/app/data'):
    DATABASE_DIR = "/app/data"
else:
    DATABASE_DIR = "data"

DATABASE_PATH = os.path.join(DATABASE_DIR, "database.db")

def migrate():
    """Add metadata tracking columns to daily_balance table"""
    if not os.path.exists(DATABASE_PATH):
        print("Database does not exist yet. Migration will be applied on first run.")
        return

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Check if daily_balance table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_balance'")
        if not cursor.fetchone():
            print("daily_balance table does not exist yet. Skipping migration.")
            conn.close()
            return

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(daily_balance)")
        columns = [column[1] for column in cursor.fetchall()]

        # Add created_by_user_id column if it doesn't exist
        if "created_by_user_id" not in columns:
            cursor.execute("""
                ALTER TABLE daily_balance
                ADD COLUMN created_by_user_id INTEGER
                REFERENCES users(id) ON DELETE SET NULL
            """)
            print("✓ Added created_by_user_id column to daily_balance")

        # Add created_by_source column if it doesn't exist
        if "created_by_source" not in columns:
            cursor.execute("""
                ALTER TABLE daily_balance
                ADD COLUMN created_by_source TEXT DEFAULT 'user'
            """)
            print("✓ Added created_by_source column to daily_balance")

        # Add edited_by_user_id column if it doesn't exist
        if "edited_by_user_id" not in columns:
            cursor.execute("""
                ALTER TABLE daily_balance
                ADD COLUMN edited_by_user_id INTEGER
                REFERENCES users(id) ON DELETE SET NULL
            """)
            print("✓ Added edited_by_user_id column to daily_balance")

        # Add finalized_at column if it doesn't exist
        if "finalized_at" not in columns:
            cursor.execute("""
                ALTER TABLE daily_balance
                ADD COLUMN finalized_at TEXT
            """)
            print("✓ Added finalized_at column to daily_balance")

        conn.commit()
        print("✓ Migration F completed successfully")

    except Exception as e:
        conn.rollback()
        print(f"✗ Migration F failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
