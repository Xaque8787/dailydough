import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

LOG_DIR = Path("data/logs")
LOG_FILE = LOG_DIR / "error_log.txt"

def setup_error_logging(max_bytes=10485760, backup_count=5, log_level=logging.ERROR):
    """
    Configure rotating file handler for error logging.

    Args:
        max_bytes: Maximum size of log file before rotation (default 10MB)
        backup_count: Number of backup files to keep (default 5)
        log_level: Minimum log level to capture (default ERROR)
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )

    file_handler.setLevel(log_level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)

    if root_logger.level > log_level:
        root_logger.setLevel(log_level)

    return file_handler


def get_log_files():
    """Get all log files (main and rotated)."""
    if not LOG_DIR.exists():
        return []

    log_files = []
    if LOG_FILE.exists():
        log_files.append(LOG_FILE)

    for i in range(1, 100):
        rotated_file = Path(f"{LOG_FILE}.{i}")
        if rotated_file.exists():
            log_files.append(rotated_file)
        else:
            break

    return log_files


def read_log_file(file_path, max_lines=1000):
    """
    Read log file and return lines in reverse order (newest first).

    Args:
        file_path: Path to log file
        max_lines: Maximum number of lines to return

    Returns:
        List of log lines (newest first)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return lines[-max_lines:][::-1]
    except Exception as e:
        logging.error(f"Error reading log file {file_path}: {e}")
        return []


def get_log_stats():
    """Get statistics about log files."""
    log_files = get_log_files()

    total_size = 0
    file_info = []

    for log_file in log_files:
        size = log_file.stat().st_size
        total_size += size
        file_info.append({
            'name': log_file.name,
            'path': str(log_file),
            'size': size,
            'size_mb': round(size / (1024 * 1024), 2)
        })

    return {
        'total_files': len(log_files),
        'total_size': total_size,
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'files': file_info
    }
