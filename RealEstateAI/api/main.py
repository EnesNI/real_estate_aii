from __future__ import annotations

from fastapi import FastAPI

from api.routes import Services, create_router
from core.config import get_settings
from core.security import TokenStore
from database.db import DatabaseManager, init_db
from ml.model import PredictionEngine
from services.auth_service import AuthService, UserManager
from services.prediction_service import PredictionService
from services.property_service import PropertyManager
from services.scraper_service import ScraperService

settings = get_settings()

db_manager = DatabaseManager()
init_db(db_manager)

property_manager = PropertyManager(db_manager)
property_manager.seed_from_csv(settings.data_dir / "housing_data.csv")

user_manager = UserManager(db_manager)

token_store = TokenStore()
auth_service = AuthService(user_manager, token_store, settings.token_ttl_minutes)

prediction_engine = PredictionEngine()
prediction_service = PredictionService(db_manager, prediction_engine)

scraper_service = ScraperService(property_manager)

services = Services(
    auth_service=auth_service,
    property_manager=property_manager,
    prediction_service=prediction_service,
    scraper_service=scraper_service,
)

app = FastAPI(title="RealEstate Predict API", version="1.0.0")
app.include_router(create_router(services))


@app.on_event("startup")
def on_startup() -> None:
    """Warm up the ML model on API startup."""

    prediction_engine.ensure_model()
