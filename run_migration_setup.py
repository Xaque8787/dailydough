#!/usr/bin/env python3
"""
Run this script to set up the database and apply the multi-position migration.
This should be run once after updating to the multi-position version.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, database_exists

print("=" * 60)
print("Multi-Position & Inactive Status Migration")
print("=" * 60)

if not database_exists():
    print("\n📦 Database does not exist. Creating new database with updated schema...")
    init_db()
    print("✅ Database created successfully!")
    print("\nℹ️  No migration needed - database was created with the new schema.")
else:
    print("\n📊 Existing database found. Running migration...")
    print("-" * 60)

    import subprocess
    result = subprocess.run(
        ['python3', 'migrations/add_multi_position_and_inactive_status.py'],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print("⚠️  Errors:", result.stderr)

    if result.returncode == 0:
        print("-" * 60)
        print("✅ Migration completed successfully!")
    else:
        print("-" * 60)
        print("❌ Migration failed with exit code", result.returncode)
        sys.exit(1)

print("\n" + "=" * 60)
print("Setup Complete!")
print("=" * 60)
print("\nYou can now:")
print("  • Add multiple positions to employees")
print("  • Set different schedules per position")
print("  • Mark employees as inactive")
print("  • All historical data has been preserved")
print()
