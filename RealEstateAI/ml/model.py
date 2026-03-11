from __future__ import annotations

from pathlib import Path
import pickle
from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from core.config import ensure_directories, get_settings
from utils.data_processing import load_housing_data, prepare_training_data


class ModelNotReadyError(RuntimeError):
    """Raised when predictions are requested before the model is ready."""


class PredictionEngine:
    """Machine learning engine for property price prediction."""

    def __init__(self, model_path: Path | None = None) -> None:
        settings = get_settings()
        self.model_path = Path(model_path) if model_path else settings.model_path
        self.pipeline: Pipeline | None = None

    def train(self, data_path: Path | None = None) -> float:
        """Train the model and return MAE on a validation split."""

        settings = get_settings()
        path = data_path or settings.data_dir / "housing_data.csv"
        df = load_housing_data(path)
        features, target = prepare_training_data(df)

        preprocessor = ColumnTransformer(
            transformers=[
                ("location", OneHotEncoder(handle_unknown="ignore"), ["location"]),
                ("numeric", "passthrough", ["size", "bedrooms", "bathrooms", "year_built"]),
            ]
        )

        regressor = RandomForestRegressor(n_estimators=200, random_state=42)

        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", regressor),
        ])

        x_train, x_test, y_train, y_test = train_test_split(
            features, target, test_size=0.2, random_state=42
        )

        pipeline.fit(x_train, y_train)
        predictions = pipeline.predict(x_test)
        mae = mean_absolute_error(y_test, predictions)

        self.pipeline = pipeline
        self.save()
        return float(mae)

    def save(self) -> None:
        """Persist trained model to disk."""

        if self.pipeline is None:
            raise ModelNotReadyError("Model is not trained.")
        ensure_directories()
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        with self.model_path.open("wb") as handle:
            pickle.dump(self.pipeline, handle)

    def load(self) -> None:
        """Load model from disk."""

        if not self.model_path.exists():
            raise ModelNotReadyError("Model file not found.")
        with self.model_path.open("rb") as handle:
            self.pipeline = pickle.load(handle)

    def ensure_model(self) -> None:
        """Ensure the model is ready for inference."""

        if self.pipeline is not None:
            return
        if self.model_path.exists():
            self.load()
        else:
            self.train()

    def _normalize_features(self, features: dict[str, Any]) -> dict[str, Any]:
        data = dict(features)
        if "square_feet" in data and "size" not in data:
            data["size"] = data.pop("square_feet")
        if "city" in data and "location" not in data:
            data["location"] = data.pop("city")
        return data

    def predict(self, features: dict[str, Any]) -> float:
        """Predict price for a single property input."""

        self.ensure_model()
        if self.pipeline is None:
            raise ModelNotReadyError("Model is not ready.")
        normalized = self._normalize_features(features)
        df = pd.DataFrame([normalized])
        prediction = float(self.pipeline.predict(df)[0])
        return round(prediction, 2)

    def predict_batch(self, features_df: pd.DataFrame) -> list[float]:
        """Predict prices for a batch of records."""

        self.ensure_model()
        if self.pipeline is None:
            raise ModelNotReadyError("Model is not ready.")
        predictions = self.pipeline.predict(features_df)
        return [float(value) for value in predictions]

    def future_price(self, price: float, growth: float = 0.04, years: int = 5) -> float:
        """Project future price using compounded growth."""

        future = price
        for _ in range(years):
            future *= (1 + growth)
        return round(future, 2)
