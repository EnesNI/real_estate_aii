from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from typing import Sequence

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "database"
MODEL_DIR = BASE_DIR / "ml" / "artifacts"
LOG_DIR = BASE_DIR / "logs"

DEFAULT_DB_PATH = DB_DIR / "realestate.db"
DEFAULT_MODEL_PATH = MODEL_DIR / "price_model.pkl"

DEFAULT_SCRAPE_URLS = [
    "https://example.com/real-estate-listings"
]

API_HOST = os.getenv("REAL_ESTATE_API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("REAL_ESTATE_API_PORT", "8000"))
API_BASE_URL = os.getenv("REAL_ESTATE_API_URL", f"http://{API_HOST}:{API_PORT}")

TOKEN_TTL_MINUTES = int(os.getenv("REAL_ESTATE_TOKEN_TTL", "120"))


@dataclass(frozen=True)
class Settings:
    """Application settings with sensible defaults."""

    base_dir: Path = BASE_DIR
    data_dir: Path = DATA_DIR
    db_path: Path = DEFAULT_DB_PATH
    model_path: Path = DEFAULT_MODEL_PATH
    api_base_url: str = API_BASE_URL
    token_ttl_minutes: int = TOKEN_TTL_MINUTES
    scrape_urls: Sequence[str] = tuple(DEFAULT_SCRAPE_URLS)


def ensure_directories() -> None:
    """Ensure required directories exist."""

    for path in (DB_DIR, MODEL_DIR, LOG_DIR):
        path.mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    """Return immutable settings."""

    return Settings()
