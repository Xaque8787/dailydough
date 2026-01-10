import os
import shutil
from datetime import datetime
from typing import List, Dict
import sqlite3
from app.database import DATABASE_PATH


def create_backup() -> str:
    backups_dir = "data/backups"
    if not os.path.exists(backups_dir):
        os.makedirs(backups_dir)

    if not os.path.exists(DATABASE_PATH):
        raise FileNotFoundError("Database file not found")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{timestamp}.db"
    filepath = os.path.join(backups_dir, filename)

    src_conn = None
    dst_conn = None

    try:
        src_conn = sqlite3.connect(DATABASE_PATH)
        dst_conn = sqlite3.connect(filepath)

        with src_conn:
            src_conn.backup(dst_conn)

        dst_conn.close()
        src_conn.close()

        if not os.path.exists(filepath):
            raise Exception("Backup file was not created")

        if os.path.getsize(filepath) == 0:
            os.remove(filepath)
            raise Exception("Backup file is empty")

        return filename

    except Exception as e:
        if dst_conn:
            dst_conn.close()
        if src_conn:
            src_conn.close()

        if os.path.exists(filepath):
            os.remove(filepath)

        raise Exception(f"Backup failed: {str(e)}")


def list_backups() -> List[Dict[str, any]]:
    backups_dir = "data/backups"

    if not os.path.exists(backups_dir):
        return []

    backups = []
    for filename in os.listdir(backups_dir):
        if filename.endswith('.db'):
            filepath = os.path.join(backups_dir, filename)
            stat = os.stat(filepath)
            backups.append({
                'filename': filename,
                'size': stat.st_size,
                'created_at': datetime.fromtimestamp(stat.st_mtime)
            })

    backups.sort(key=lambda x: x['created_at'], reverse=True)

    return backups[:7]


def delete_backup(filename: str) -> bool:
    backups_dir = "data/backups"
    filepath = os.path.join(backups_dir, filename)

    if not filename.endswith('.db'):
        return False

    if '..' in filename or '/' in filename:
        return False

    if os.path.exists(filepath):
        os.remove(filepath)
        return True

    return False


def get_backup_path(filename: str) -> str:
    backups_dir = "data/backups"

    if not filename.endswith('.db'):
        raise ValueError("Invalid filename")

    if '..' in filename or '/' in filename:
        raise ValueError("Invalid filename")

    filepath = os.path.join(backups_dir, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError("Backup file not found")

    return filepath
