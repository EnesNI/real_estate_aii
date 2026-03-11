from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass
from typing import Dict, Optional


_HASH_ITERATIONS = 120_000


def _encode_bytes(value: bytes) -> str:
    return base64.b64encode(value).decode("utf-8")


def _decode_bytes(value: str) -> bytes:
    return base64.b64decode(value.encode("utf-8"))


def hash_password(password: str) -> str:
    """Hash a password with PBKDF2 and return a serialized hash string."""

    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _HASH_ITERATIONS)
    return f"{_HASH_ITERATIONS}${_encode_bytes(salt)}${_encode_bytes(dk)}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against the stored hash string."""

    try:
        iterations_str, salt_b64, hash_b64 = stored_hash.split("$", 2)
        iterations = int(iterations_str)
        salt = _decode_bytes(salt_b64)
        stored = _decode_bytes(hash_b64)
    except ValueError:
        return False

    new_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(new_hash, stored)


@dataclass
class TokenRecord:
    user_id: int
    expires_at: float


class TokenStore:
    """In-memory token store for session management."""

    def __init__(self) -> None:
        self._tokens: Dict[str, TokenRecord] = {}

    def create_token(self, user_id: int, ttl_minutes: int) -> str:
        token = secrets.token_urlsafe(32)
        expires_at = time.time() + ttl_minutes * 60
        self._tokens[token] = TokenRecord(user_id=user_id, expires_at=expires_at)
        return token

    def validate_token(self, token: str) -> Optional[int]:
        record = self._tokens.get(token)
        if record is None:
            return None
        if record.expires_at < time.time():
            self._tokens.pop(token, None)
            return None
        return record.user_id

    def revoke_token(self, token: str) -> None:
        self._tokens.pop(token, None)

    def purge_expired(self) -> int:
        now = time.time()
        expired = [key for key, record in self._tokens.items() if record.expires_at < now]
        for key in expired:
            self._tokens.pop(key, None)
        return len(expired)
