"""
Add Cloud Backup Providers Table

Creates the backup_providers table which stores configuration for S3-compatible
cloud backup destinations (Backblaze B2, AWS S3, Cloudflare R2, MinIO, etc.).

New Tables:
  - backup_providers
      - id              INTEGER PRIMARY KEY AUTOINCREMENT
      - name            TEXT NOT NULL            — user-facing label for this provider
      - provider_type   TEXT NOT NULL DEFAULT 's3' — always 's3'; reserved for future types
      - access_key_enc  TEXT NOT NULL            — Fernet-encrypted access key
      - secret_key_enc  TEXT NOT NULL            — Fernet-encrypted secret key
      - endpoint        TEXT NOT NULL            — S3-compatible endpoint URL
      - bucket_name     TEXT NOT NULL            — target bucket name
      - region          TEXT                     — optional region (empty for B2)
      - path_prefix     TEXT NOT NULL DEFAULT 'db-backups/' — folder prefix inside bucket
      - is_active       INTEGER NOT NULL DEFAULT 1
      - created_at      TEXT NOT NULL DEFAULT (datetime('now'))
      - updated_at      TEXT NOT NULL DEFAULT (datetime('now'))

Security:
  Credentials are stored encrypted at rest using Fernet symmetric encryption
  keyed from the application SECRET_KEY. Raw credentials are never persisted.
"""

MIGRATION_ID = "2026_05_07_add_cloud_backup_providers"


def upgrade(conn, column_exists, table_exists):
    if not table_exists("backup_providers"):
        conn.execute("""
            CREATE TABLE backup_providers (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT NOT NULL,
                provider_type   TEXT NOT NULL DEFAULT 's3',
                access_key_enc  TEXT NOT NULL,
                secret_key_enc  TEXT NOT NULL,
                endpoint        TEXT NOT NULL,
                bucket_name     TEXT NOT NULL,
                region          TEXT,
                path_prefix     TEXT NOT NULL DEFAULT 'db-backups/',
                is_active       INTEGER NOT NULL DEFAULT 1,
                created_at      TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        print("  ✓ Created backup_providers table")
    else:
        print("  → backup_providers table already exists, skipping")
