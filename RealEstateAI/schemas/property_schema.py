from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


class PropertyBase(BaseModel):
    """Base property schema."""

    address: str = Field(..., min_length=3)
    city: str = Field(..., min_length=2)
    state: str = Field(..., min_length=2, max_length=2)
    zipcode: str = Field(..., min_length=4, max_length=10)
    square_feet: float = Field(..., gt=0)
    bedrooms: int = Field(..., ge=0)
    bathrooms: float = Field(..., ge=0)
    year_built: int = Field(..., ge=1800, le=2100)
    last_sale_price: Optional[float] = Field(default=None, ge=0)
    last_sale_date: Optional[str] = None


class PropertyCreate(PropertyBase):
    """Schema for creating properties."""

    pass


class PropertyOut(PropertyBase):
    """Schema returned for property records."""

    id: int
    created_at: str

    model_config = {"from_attributes": True}


class PropertySearch(BaseModel):
    """Search filters for property queries."""

    city: Optional[str] = None
    state: Optional[str] = None
    min_price: Optional[float] = Field(default=None, ge=0)
    max_price: Optional[float] = Field(default=None, ge=0)
    min_sqft: Optional[float] = Field(default=None, ge=0)
    max_sqft: Optional[float] = Field(default=None, ge=0)
    bedrooms: Optional[int] = Field(default=None, ge=0)
    bathrooms: Optional[float] = Field(default=None, ge=0)


class AmenityResponse(BaseModel):
    """Nearby amenities response."""

    city: str
    amenities: list[str]


class ScrapeRequest(BaseModel):
    """Optional payload for scraping listing URLs."""

    urls: Optional[list[str]] = None
