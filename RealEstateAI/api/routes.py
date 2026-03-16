from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status

from core.config import get_settings
from models.user import User
from schemas.prediction_schema import MarketTrendsOut, PredictionOut, PredictionRequest
from schemas.property_schema import AmenityResponse, PropertyOut, PropertySearch, ScrapeRequest
from schemas.user_schema import AuthResponse, UserCreate, UserLogin, UserOut, UserProfile
from services.auth_service import AuthService
from services.prediction_service import PredictionService
from services.property_service import PropertyManager
from services.scraper_service import ScraperService
from utils.helpers import get_amenities


@dataclass
class Services:
    """Container for shared service instances."""

    auth_service: AuthService
    property_manager: PropertyManager
    prediction_service: PredictionService
    scraper_service: ScraperService


def _extract_token(authorization: Optional[str]) -> str:
    """Extract bearer token from the Authorization header."""

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token.")
    return authorization.split(" ", 1)[1]


def create_router(services: Services) -> APIRouter:
    """Create API routes with injected services."""

    router = APIRouter()

    def get_current_user(authorization: Optional[str] = Header(default=None)) -> User:
        """Resolve the current user from the auth token."""

        token = _extract_token(authorization)
        try:
            return services.auth_service.require_user(token)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    @router.post("/register", response_model=UserOut)
    def register(payload: UserCreate) -> UserOut:
        """Register a new user account."""

        try:
            user = services.auth_service.register(payload.username, payload.email, payload.password)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        return UserOut(**user.__dict__)

    @router.post("/login", response_model=AuthResponse)
    def login(payload: UserLogin) -> AuthResponse:
        """Authenticate a user and return a session token."""

        try:
            session = services.auth_service.login(payload.username, payload.password)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        return AuthResponse(token=session.token, user=UserOut(**session.user.__dict__))

    @router.get("/properties", response_model=list[PropertyOut])
    def list_properties(
        city: Optional[str] = None,
        state: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_sqft: Optional[float] = None,
        max_sqft: Optional[float] = None,
        bedrooms: Optional[int] = None,
        bathrooms: Optional[float] = None,
    ) -> list[PropertyOut]:
        """Search for properties with optional filters."""

        filters = PropertySearch(
            city=city,
            state=state,
            min_price=min_price,
            max_price=max_price,
            min_sqft=min_sqft,
            max_sqft=max_sqft,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
        )
        properties = services.property_manager.search_properties(filters)
        return [PropertyOut(**prop.__dict__) for prop in properties]

    @router.post("/predict", response_model=PredictionOut)
    def predict_price(
        payload: PredictionRequest,
        current_user: User = Depends(get_current_user),
    ) -> PredictionOut:
        """Generate and store a price prediction for the current user."""

        prediction = services.prediction_service.predict_and_store(current_user.id, payload)
        return PredictionOut(**prediction.__dict__)

    @router.post("/predict-growth", response_model=PredictionOut)
    def predict_growth(payload: PredictionRequest) -> PredictionOut:
        """Predict price growth for a property."""

        try:
            prediction = services.prediction_service.predict_growth(payload)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        return PredictionOut(**prediction.__dict__)

    @router.get("/predictions", response_model=list[PredictionOut])
    def get_predictions(current_user: User = Depends(get_current_user)) -> list[PredictionOut]:
        """Return prediction history for the current user."""

        predictions = services.prediction_service.list_predictions(current_user.id)
        return [PredictionOut(**prediction.__dict__) for prediction in predictions]

    @router.get("/market-trends", response_model=MarketTrendsOut)
    def market_trends() -> MarketTrendsOut:
        """Return summary market trend statistics."""

        settings = get_settings()
        trends = services.property_manager.get_market_trends(settings.data_dir / "housing_data.csv")
        return MarketTrendsOut(**trends)

    @router.get("/amenities", response_model=AmenityResponse)
    def amenities(city: str) -> AmenityResponse:
        """Return nearby amenities for a given city."""

        return AmenityResponse(city=city, amenities=get_amenities(city))

    @router.post("/scrape")
    def scrape(payload: Optional[ScrapeRequest] = None) -> dict[str, int]:
        """Scrape listing sources and store new property records."""

        settings = get_settings()
        urls = payload.urls if payload and payload.urls else list(settings.scrape_urls)
        added = services.scraper_service.scrape_and_store(urls)
        return {"added": added}

    @router.get("/profile", response_model=UserProfile)
    def profile(current_user: User = Depends(get_current_user)) -> UserProfile:
        """Return the current user's profile summary."""

        count = services.auth_service.user_manager.count_predictions(current_user.id)
        return UserProfile(user=UserOut(**current_user.__dict__), prediction_count=count)

    return router
