from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Prediction:
    """Domain model for stored predictions."""

    id: int
    user_id: int
    property_id: int | None
    input_data: dict[str, Any]
    predicted_price: float
    future_price: float
    created_at: str
