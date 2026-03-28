import hashlib
import os
import hmac


def hash_password(password: str, salt: bytes = None):
    if salt is None:
        salt = os.urandom(16)
    pw = password.encode('utf-8')
    dk = hashlib.pbkdf2_hmac('sha256', pw, salt, 100000)
    return salt.hex() + ':' + dk.hex()


def verify_password(stored: str, provided: str) -> bool:
    try:
        salt_hex, dk_hex = stored.split(':')
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(dk_hex)
        test = hashlib.pbkdf2_hmac('sha256', provided.encode('utf-8'), salt, 100000)
        return hmac.compare_digest(test, expected)
    except Exception:
        return False
