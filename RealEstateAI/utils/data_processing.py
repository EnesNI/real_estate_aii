from __future__ import annotations

from pathlib import Path
from typing import Iterable
import pandas as pd


def load_housing_data(path: Path) -> pd.DataFrame:
    """Load and clean housing data."""

    df = pd.read_csv(path)
    return clean_property_dataframe(df)


def clean_property_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean housing data by handling missing values and normalizing text."""

    cleaned = df.copy()
    if "location" in cleaned.columns:
        cleaned["location"] = cleaned["location"].astype(str).str.strip()

    numeric_columns = [
        col for col in ["size", "bedrooms", "bathrooms", "year_built", "price"] if col in cleaned.columns
    ]

    for col in numeric_columns:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")
        median_value = cleaned[col].median()
        cleaned[col] = cleaned[col].fillna(median_value)

    cleaned = cleaned.dropna(subset=["location"])
    return cleaned


def prepare_training_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Split housing data into features and target."""

    features = df.drop(columns=["price"])
    target = df["price"]
    return features, target


def normalize_features(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    """Normalize numeric columns to 0-1 range."""

    normalized = df.copy()
    for column in columns:
        min_value = normalized[column].min()
        max_value = normalized[column].max()
        if max_value == min_value:
            normalized[column] = 0.0
        else:
            normalized[column] = (normalized[column] - min_value) / (max_value - min_value)
    return normalized
