import os
import re
import subprocess
import tempfile
from app.utils.encryption import decrypt

# Allowlist pattern for bucket names and path prefixes — prevents path traversal
_SAFE_NAME_RE = re.compile(r'^[a-zA-Z0-9._/\-]{1,512}$')

BACKUP_SOURCE_DIR = "data/backups"


def _validate_name(value: str, field: str) -> None:
    if not _SAFE_NAME_RE.match(value):
        raise ValueError(f"Invalid characters in {field}: {value!r}")


def _build_rclone_config(access_key: str, secret_key: str, endpoint: str, region: str | None) -> str:
    if "backblazeb2.com" in endpoint:
        provider = "Backblaze"
    else:
        provider = "Other"
    lines = [
        "[remote]",
        "type = s3",
        f"provider = {provider}",
        f"access_key_id = {access_key}",
        f"secret_access_key = {secret_key}",
        f"endpoint = {endpoint}",
    ]
    if region:
        lines.append(f"region = {region}")
    return "\n".join(lines) + "\n"


def _run_rclone(args: list[str], config_content: str) -> tuple[int, str, str]:
    """
    Write a temp config, run rclone with the given args, delete config in finally.
    Returns (returncode, stdout, stderr).
    """
    tmp_dir = tempfile.mkdtemp()
    config_path = os.path.join(tmp_dir, "rclone.conf")
    os.chmod(tmp_dir, 0o700)
    try:
        with open(config_path, "w") as f:
            f.write(config_content)
        os.chmod(config_path, 0o600)

        cmd = ["rclone"] + args + ["--config", config_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.returncode, result.stdout, result.stderr
    finally:
        if os.path.exists(config_path):
            os.remove(config_path)
        if os.path.exists(tmp_dir):
            os.rmdir(tmp_dir)


def test_connection(provider) -> dict:
    """
    Test that credentials are valid by listing buckets on the remote.
    Returns {"success": bool, "message": str}.
    """
    try:
        access_key = decrypt(provider.access_key_enc)
        secret_key = decrypt(provider.secret_key_enc)
        config = _build_rclone_config(access_key, secret_key, provider.endpoint, provider.region)
        returncode, stdout, stderr = _run_rclone(["lsd", "remote:"], config)
        if returncode == 0:
            return {"success": True, "message": "Connection successful"}
        return {"success": False, "message": stderr.strip() or "Connection failed"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def verify_bucket(provider) -> dict:
    """
    Verify the configured bucket is accessible by listing its top level.
    Returns {"success": bool, "message": str}.
    """
    try:
        _validate_name(provider.bucket_name, "bucket_name")
        access_key = decrypt(provider.access_key_enc)
        secret_key = decrypt(provider.secret_key_enc)
        config = _build_rclone_config(access_key, secret_key, provider.endpoint, provider.region)
        returncode, stdout, stderr = _run_rclone(
            ["ls", f"remote:{provider.bucket_name}", "--max-depth", "1"],
            config
        )
        if returncode == 0:
            return {"success": True, "message": "Bucket is accessible"}
        return {"success": False, "message": stderr.strip() or "Bucket not accessible"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def create_bucket(provider) -> dict:
    """
    Create the configured bucket. Returns {"success": bool, "message": str}.
    """
    try:
        _validate_name(provider.bucket_name, "bucket_name")
        access_key = decrypt(provider.access_key_enc)
        secret_key = decrypt(provider.secret_key_enc)
        config = _build_rclone_config(access_key, secret_key, provider.endpoint, provider.region)
        returncode, stdout, stderr = _run_rclone(
            ["mkdir", f"remote:{provider.bucket_name}"],
            config
        )
        if returncode == 0:
            return {"success": True, "message": "Bucket created successfully"}
        return {"success": False, "message": stderr.strip() or "Failed to create bucket"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def run_backup(provider) -> dict:
    """
    Copy data/backups to the remote bucket under path_prefix.
    Returns {"success": bool, "message": str, "output": str}.
    """
    try:
        _validate_name(provider.bucket_name, "bucket_name")
        _validate_name(provider.path_prefix, "path_prefix")
        access_key = decrypt(provider.access_key_enc)
        secret_key = decrypt(provider.secret_key_enc)
        config = _build_rclone_config(access_key, secret_key, provider.endpoint, provider.region)

        destination = f"remote:{provider.bucket_name}/{provider.path_prefix.rstrip('/')}"
        returncode, stdout, stderr = _run_rclone(
            ["copy", BACKUP_SOURCE_DIR, destination, "--transfers", "4", "--verbose"],
            config
        )
        combined = (stdout + "\n" + stderr).strip()
        if returncode == 0:
            return {"success": True, "message": "Backup completed successfully", "output": combined}
        return {"success": False, "message": stderr.strip() or "Backup failed", "output": combined}
    except Exception as e:
        return {"success": False, "message": str(e), "output": ""}
