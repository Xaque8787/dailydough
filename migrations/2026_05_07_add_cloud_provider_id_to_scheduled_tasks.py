"""
Add cloud_provider_id to scheduled_tasks

Allows a scheduled task of type 'cloud_backup' to reference a BackupProvider
so the scheduler knows which S3-compatible provider to run the backup against.

Changes:
  - scheduled_tasks.cloud_provider_id (INTEGER, nullable, FK to backup_providers.id)
"""

MIGRATION_ID = "2026_05_07_add_cloud_provider_id_to_scheduled_tasks"


def upgrade(conn, column_exists, table_exists):
    if not table_exists("scheduled_tasks"):
        return

    if not column_exists("scheduled_tasks", "cloud_provider_id"):
        conn.execute(
            "ALTER TABLE scheduled_tasks ADD COLUMN cloud_provider_id INTEGER "
            "REFERENCES backup_providers(id)"
        )
        print("  + scheduled_tasks.cloud_provider_id added")
