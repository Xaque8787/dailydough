"""
Migration: Add include_in_payroll_summary column to tip_entry_requirements

This migration adds a new boolean column 'include_in_payroll_summary' to the tip_entry_requirements table.
This attribute allows tip requirement data to be included in a separate "Payroll Summary" section
of tip reports for easier payroll processing.

Database Location:
- Docker: /app/data/database.db
- Bare metal: <project_root>/data/database.db

Usage:
    python migrations/add_include_in_payroll_summary.py
"""

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

if os.path.exists("/app"):
    os.chdir("/app")
else:
    os.chdir(project_root)

sys.path.insert(0, project_root)

from sqlalchemy import inspect, text
from app.database import engine

def run_migration():
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('tip_entry_requirements')]

    if 'include_in_payroll_summary' not in columns:
        print("Adding 'include_in_payroll_summary' column to tip_entry_requirements table...")
        with engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE tip_entry_requirements
                ADD COLUMN include_in_payroll_summary BOOLEAN DEFAULT 0;
            """))
            conn.commit()
        print("✓ Migration completed: include_in_payroll_summary column added")
    else:
        print("✓ Column 'include_in_payroll_summary' already exists, skipping migration")

if __name__ == "__main__":
    run_migration()
