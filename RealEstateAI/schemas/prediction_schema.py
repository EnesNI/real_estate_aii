from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


class PredictionRequest(BaseModel):
    """Payload for property price prediction."""

    location: str = Field(..., min_length=2)
    square_feet: float = Field(..., gt=0)
    bedrooms: int = Field(..., ge=0)
    bathrooms: float = Field(..., ge=0)
    year_built: int = Field(..., ge=1800, le=2100)
    property_id: Optional[int] = None


class PredictionOut(BaseModel):
    """Prediction response with stored metadata."""

    id: int
    user_id: int
    property_id: Optional[int]
    predicted_price: float
    future_price: float
    created_at: str
    input_data: dict

    model_config = {"from_attributes": True}


class MarketTrendsOut(BaseModel):
    """Market trend summary statistics."""

    average_price: float
    median_price: float
    min_price: float
    max_price: float
    average_price_by_city: dict[str, float]
    sample_size: int
