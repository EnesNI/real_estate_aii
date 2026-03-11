from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.security import TokenStore, hash_password, verify_password
from database.db import DatabaseManager, row_to_dict
from models.user import User


class UserManager:
    """Manage user CRUD and authentication."""

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def register_user(self, username: str, email: str, password: str) -> User:
        """Create a new user account."""

        existing = self.db.query_one(
            "SELECT id FROM users WHERE username = ? OR email = ?", (username, email)
        )
        if existing:
            raise ValueError("User already exists.")

        hashed_password = hash_password(password)
        created_at = datetime.utcnow().isoformat()
        user_id = self.db.execute(
            "INSERT INTO users(username, email, hashed_password, created_at) VALUES(?, ?, ?, ?)",
            (username, email, hashed_password, created_at),
        )
        return User(
            id=user_id,
            username=username,
            email=email,
            hashed_password=hashed_password,
            created_at=created_at,
        )

    def authenticate(self, username: str, password: str) -> User:
        """Validate credentials and return the matching user."""

        row = self.db.query_one("SELECT * FROM users WHERE username = ?", (username,))
        if row is None:
            raise ValueError("Invalid username or password.")
        user_data = row_to_dict(row)
        if not verify_password(password, user_data["hashed_password"]):
            raise ValueError("Invalid username or password.")
        return User(**user_data)

    def get_user_by_id(self, user_id: int) -> User:
        """Fetch a user by id."""

        row = self.db.query_one("SELECT * FROM users WHERE id = ?", (user_id,))
        if row is None:
            raise ValueError("User not found.")
        return User(**row_to_dict(row))

    def count_predictions(self, user_id: int) -> int:
        """Return prediction count for a user."""

        row = self.db.query_one(
            "SELECT COUNT(*) as count FROM predictions WHERE user_id = ?", (user_id,)
        )
        if row is None:
            return 0
        return int(row["count"])


@dataclass
class AuthSession:
    """Authenticated session info."""

    user: User
    token: str


class AuthService:
    """Service for login, token management, and authorization checks."""

    def __init__(self, user_manager: UserManager, token_store: TokenStore, ttl_minutes: int) -> None:
        self.user_manager = user_manager
        self.token_store = token_store
        self.ttl_minutes = ttl_minutes

    def register(self, username: str, email: str, password: str) -> User:
        """Register a new user account."""

        return self.user_manager.register_user(username, email, password)

    def login(self, username: str, password: str) -> AuthSession:
        """Authenticate a user and issue a session token."""

        user = self.user_manager.authenticate(username, password)
        token = self.token_store.create_token(user.id, self.ttl_minutes)
        return AuthSession(user=user, token=token)

    def require_user(self, token: str) -> User:
        """Validate a token and return its user."""

        user_id = self.token_store.validate_token(token)
        if user_id is None:
            raise ValueError("Invalid or expired token.")
        return self.user_manager.get_user_by_id(user_id)

    def logout(self, token: str) -> None:
        """Revoke an authentication token."""

        self.token_store.revoke_token(token)
