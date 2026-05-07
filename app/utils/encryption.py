import os
import base64
import hashlib
from cryptography.fernet import Fernet


def _get_fernet() -> Fernet:
    secret_key = os.environ.get("SECRET_KEY", "")
    if not secret_key:
        raise RuntimeError("SECRET_KEY environment variable is not set")
    # Derive a 32-byte key from the app secret using SHA-256, then base64-url encode it
    key_bytes = hashlib.sha256(secret_key.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)


def encrypt(plaintext: str) -> str:
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    return _get_fernet().decrypt(ciphertext.encode()).decode()
