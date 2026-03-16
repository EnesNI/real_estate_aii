from __future__ import annotations

from datetime import datetime
import json

from database.db import DatabaseManager, row_to_dict
from ml.model import PredictionEngine
from models.prediction import Prediction
from schemas.prediction_schema import PredictionRequest


class PredictionService:
    """Service for running and storing model predictions."""

    def __init__(self, db: DatabaseManager, engine: PredictionEngine) -> None:
        self.db = db
        self.engine = engine

    def predict_and_store(self, user_id: int, request: PredictionRequest) -> Prediction:
        """Run a prediction and store the result in the database."""

        input_data = {
            "location": request.location,
            "square_feet": request.square_feet,
            "bedrooms": request.bedrooms,
            "bathrooms": request.bathrooms,
            "year_built": request.year_built,
        }
        predicted_price = self.engine.predict(input_data)
        future_price = self.engine.future_price(predicted_price)

        created_at = datetime.utcnow().isoformat()
        prediction_id = self.db.execute(
            """
            INSERT INTO predictions(
                user_id, property_id, input_data, predicted_price, future_price, created_at
            ) VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                request.property_id,
                json.dumps(input_data),
                predicted_price,
                future_price,
                created_at,
            ),
        )

        return Prediction(
            id=prediction_id,
            user_id=user_id,
            property_id=request.property_id,
            input_data=input_data,
            predicted_price=predicted_price,
            future_price=future_price,
            created_at=created_at,
        )

    def list_predictions(self, user_id: int) -> list[Prediction]:
        """List all predictions for a user."""

        rows = self.db.query(
            "SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
        predictions: list[Prediction] = []
        for row in rows:
            data = row_to_dict(row)
            data["input_data"] = json.loads(data["input_data"])
            predictions.append(Prediction(**data))
        return predictions

    def predict_growth(self, request: PredictionRequest) -> Prediction:
        """Predict price growth for a property."""

        input_data = {
            "location": request.location,
            "square_feet": request.square_feet,
            "bedrooms": request.bedrooms,
            "bathrooms": request.bathrooms,
            "year_built": request.year_built,
        }
        try:
            input_data = self.engine._normalize_features(input_data)
            predicted_price = self.engine.predict(input_data)
            future_price = self.engine.future_price(predicted_price)

            return Prediction(
                id=None,  # No database storage for this prediction
                user_id=None,  # No user association for this prediction
                property_id=None,  # No property association for this prediction
                input_data=input_data,
                predicted_price=predicted_price,
                future_price=future_price,
                created_at=datetime.utcnow().isoformat(),
            )
        except Exception as e:
            print(f"Error in predict_growth: {e}")
            raise
