from __future__ import annotations

from typing import Iterable


CITY_STATE_MAP: dict[str, tuple[str, str]] = {
    "New York": ("NY", "100"),
    "Los Angeles": ("CA", "900"),
    "Chicago": ("IL", "606"),
    "Houston": ("TX", "770"),
    "Phoenix": ("AZ", "850"),
    "Philadelphia": ("PA", "190"),
    "San Antonio": ("TX", "782"),
    "San Diego": ("CA", "921"),
    "Dallas": ("TX", "752"),
    "San Jose": ("CA", "951"),
}

DEFAULT_AMENITIES: tuple[str, ...] = (
    "Parks",
    "Public Transit",
    "Coffee Shops",
    "Grocery Stores",
    "Schools",
    "Gyms",
    "Healthcare Clinics",
)

AMENITIES_BY_CITY: dict[str, list[str]] = {
    "New York": ["Subway Access", "Central Park", "Museums", "Universities"],
    "Los Angeles": ["Metro Rail", "Beaches", "Studios", "Shopping Centers"],
    "Chicago": ["Lakefront", "Parks", "L Train", "Food Markets"],
    "Houston": ["Medical District", "Parks", "Energy Corridor", "Museums"],
}

POPULAR_AMENITIES: set[str] = {"Parks", "Schools", "Transit", "Groceries"}


def normalize_text(value: str) -> str:
    """Normalize text values for consistent storage."""

    return " ".join(value.strip().split())


def safe_int(value: object, default: int = 0) -> int:
    """Convert a value to int with safe fallback."""

    try:
        return int(float(str(value)))
    except (ValueError, TypeError):
        return default


def safe_float(value: object, default: float = 0.0) -> float:
    """Convert a value to float with safe fallback."""

    try:
        return float(str(value))
    except (ValueError, TypeError):
        return default


def parse_price(value: str) -> float:
    """Parse price strings like "$450,000" into float."""

    cleaned = value.replace("$", "").replace(",", "").strip()
    return safe_float(cleaned, default=0.0)


def get_city_state(city: str) -> tuple[str, str]:
    """Infer state and zipcode prefix for a city."""

    normalized = normalize_text(city)
    return CITY_STATE_MAP.get(normalized, ("NA", "000"))


def build_address(index: int, city: str) -> str:
    """Create a simple placeholder address for seeded data."""

    return f"{100 + index} Main St"


def get_amenities(city: str) -> list[str]:
    """Return amenities for a city, falling back to defaults."""

    normalized = normalize_text(city)
    amenities = AMENITIES_BY_CITY.get(normalized)
    if amenities:
        return amenities
    return list(DEFAULT_AMENITIES)


def chunk_list(items: Iterable[str], size: int) -> list[list[str]]:
    """Chunk a list for display purposes."""

    chunked: list[list[str]] = []
    buffer: list[str] = []
    for item in items:
        buffer.append(item)
        if len(buffer) >= size:
            chunked.append(buffer)
            buffer = []
    if buffer:
        chunked.append(buffer)
    return chunked
