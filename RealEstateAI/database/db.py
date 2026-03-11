from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Any, Iterable, Iterator, Sequence

from core.config import ensure_directories, get_settings
from database.models import ALL_TABLES, INDEXES_SQL


class DatabaseError(RuntimeError):
    """Raised when a database operation fails."""


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    """Convert a sqlite row to a plain dictionary."""

    return dict(row)


class DatabaseManager:
    """SQLite database manager with safe connection handling."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        settings = get_settings()
        self.db_path = Path(db_path) if db_path else settings.db_path
        ensure_directories()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path.as_posix())
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = self._connect()
        try:
            yield conn
            conn.commit()
        except sqlite3.Error as exc:
            conn.rollback()
            raise DatabaseError(str(exc)) from exc
        finally:
            conn.close()

    def execute(self, query: str, params: Sequence[Any] | None = None) -> int:
        with self.connect() as conn:
            cur = conn.execute(query, params or [])
            return cur.lastrowid

    def executemany(self, query: str, params_seq: Iterable[Sequence[Any]]) -> None:
        with self.connect() as conn:
            conn.executemany(query, params_seq)

    def query(self, query: str, params: Sequence[Any] | None = None) -> list[sqlite3.Row]:
        with self.connect() as conn:
            cur = conn.execute(query, params or [])
            return cur.fetchall()

    def query_one(self, query: str, params: Sequence[Any] | None = None) -> sqlite3.Row | None:
        with self.connect() as conn:
            cur = conn.execute(query, params or [])
            return cur.fetchone()


def init_db(manager: DatabaseManager | None = None) -> None:
    """Initialize database tables and indexes."""

    db = manager or DatabaseManager()
    with db.connect() as conn:
        for ddl in ALL_TABLES:
            conn.execute(ddl)
        for ddl in INDEXES_SQL:
            conn.execute(ddl)
