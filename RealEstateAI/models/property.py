from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Property:
    """Domain model for stored properties."""

    id: int
    address: str
    city: str
    state: str
    zipcode: str
    square_feet: float
    bedrooms: int
    bathrooms: float
    year_built: int
    last_sale_price: float | None
    last_sale_date: str | None
    created_at: str
