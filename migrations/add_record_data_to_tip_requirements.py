"""
Migration: Add record_data column to tip_entry_requirements

This migration adds a new boolean column 'record_data' to the tip_entry_requirements table.
This attribute allows data to be entered and recorded in the field without being added to
the "is Total" calculated entries.

Usage:
    python migrations/add_record_data_to_tip_requirements.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text
from app.database import engine

def run_migration():
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('tip_entry_requirements')]

    if 'record_data' not in columns:
        print("Adding 'record_data' column to tip_entry_requirements table...")
        with engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE tip_entry_requirements
                ADD COLUMN record_data BOOLEAN DEFAULT 0;
            """))
            conn.commit()
        print("✓ Migration completed: record_data column added")
    else:
        print("✓ Column 'record_data' already exists, skipping migration")

if __name__ == "__main__":
    run_migration()
