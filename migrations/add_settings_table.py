"""
Migration: Add Settings Table

This migration creates a settings table to store application configuration.
Initial setting: backup_retention_count (default: 7 backups)
"""

import sqlite3
import os

DATABASE_PATH = os.getenv("DATABASE_PATH", "data/tips.db")


def migrate():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Create settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert default backup retention setting (7 backups)
        cursor.execute("""
            INSERT OR IGNORE INTO settings (key, value, description)
            VALUES ('backup_retention_count', '7', 'Number of database backups to keep')
        """)

        conn.commit()
        print("✓ Settings table created successfully")
        print("✓ Default backup retention set to 7 backups")

    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {str(e)}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
