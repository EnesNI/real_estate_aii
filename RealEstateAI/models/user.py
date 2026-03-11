from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """Domain model for application users."""

    id: int
    username: str
    email: str
    hashed_password: str
    created_at: str
