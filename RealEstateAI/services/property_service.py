from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from database.db import DatabaseManager, row_to_dict
from models.property import Property
from schemas.property_schema import PropertyCreate, PropertySearch
from utils.helpers import build_address, get_city_state, normalize_text
from utils.data_processing import load_housing_data


class PropertyManager:
    """Service for property persistence and queries."""

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def _to_dict(self, item: PropertyCreate) -> dict:
        """Convert a Pydantic model to a dictionary across versions."""

        if hasattr(item, "model_dump"):
            return item.model_dump()
        return item.dict()

    def add_property(self, property_data: PropertyCreate) -> Property:
        """Insert a single property into the database."""

        created_at = datetime.utcnow().isoformat()
        property_id = self.db.execute(
            """
            INSERT INTO properties(
                address, city, state, zipcode, square_feet, bedrooms, bathrooms,
                year_built, last_sale_price, last_sale_date, created_at
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                property_data.address,
                property_data.city,
                property_data.state,
                property_data.zipcode,
                property_data.square_feet,
                property_data.bedrooms,
                property_data.bathrooms,
                property_data.year_built,
                property_data.last_sale_price,
                property_data.last_sale_date,
                created_at,
            ),
        )
        return Property(id=property_id, created_at=created_at, **self._to_dict(property_data))

    def add_properties(self, properties: Iterable[PropertyCreate]) -> int:
        """Bulk insert properties and return insert count."""

        created_at = datetime.utcnow().isoformat()
        payload = [
            (
                item.address,
                item.city,
                item.state,
                item.zipcode,
                item.square_feet,
                item.bedrooms,
                item.bathrooms,
                item.year_built,
                item.last_sale_price,
                item.last_sale_date,
                created_at,
            )
            for item in properties
        ]
        if not payload:
            return 0
        self.db.executemany(
            """
            INSERT INTO properties(
                address, city, state, zipcode, square_feet, bedrooms, bathrooms,
                year_built, last_sale_price, last_sale_date, created_at
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            payload,
        )
        return len(payload)

    def list_properties(self, limit: int = 100) -> list[Property]:
        """Return a list of properties sorted by price."""

        rows = self.db.query(
            "SELECT * FROM properties ORDER BY last_sale_price DESC LIMIT ?",
            (limit,),
        )
        return [Property(**row_to_dict(row)) for row in rows]

    def search_properties(self, filters: PropertySearch) -> list[Property]:
        """Search properties using optional filters."""

        conditions: list[str] = []
        params: list[object] = []

        if filters.city:
            conditions.append("city LIKE ?")
            params.append(f"%{normalize_text(filters.city)}%")
        if filters.state:
            conditions.append("state = ?")
            params.append(filters.state.upper())
        if filters.min_price is not None:
            conditions.append("last_sale_price >= ?")
            params.append(filters.min_price)
        if filters.max_price is not None:
            conditions.append("last_sale_price <= ?")
            params.append(filters.max_price)
        if filters.min_sqft is not None:
            conditions.append("square_feet >= ?")
            params.append(filters.min_sqft)
        if filters.max_sqft is not None:
            conditions.append("square_feet <= ?")
            params.append(filters.max_sqft)
        if filters.bedrooms is not None:
            conditions.append("bedrooms >= ?")
            params.append(filters.bedrooms)
        if filters.bathrooms is not None:
            conditions.append("bathrooms >= ?")
            params.append(filters.bathrooms)

        query = "SELECT * FROM properties"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY last_sale_price DESC"

        rows = self.db.query(query, params)
        return [Property(**row_to_dict(row)) for row in rows]

    def seed_from_csv(self, data_path: Path) -> int:
        """Seed property records from the housing dataset if empty."""

        existing = self.db.query_one("SELECT id FROM properties LIMIT 1")
        if existing is not None:
            return 0

        df = load_housing_data(data_path)
        properties: list[PropertyCreate] = []

        for index, row in df.iterrows():
            city = str(row["location"])
            state, zipcode_prefix = get_city_state(city)
            zipcode = f"{zipcode_prefix}{index:02d}"
            properties.append(
                PropertyCreate(
                    address=build_address(index, city),
                    city=city,
                    state=state,
                    zipcode=zipcode,
                    square_feet=float(row["size"]),
                    bedrooms=int(row["bedrooms"]),
                    bathrooms=float(row["bathrooms"]),
                    year_built=int(row["year_built"]),
                    last_sale_price=float(row["price"]),
                    last_sale_date=f"{int(row['year_built'])}-06-01",
                )
            )

        return self.add_properties(properties)

    def get_market_trends(self, data_path: Path) -> dict[str, object]:
        """Compute aggregated market trend statistics."""

        df = load_housing_data(data_path)
        average_price = float(df["price"].mean())
        median_price = float(df["price"].median())
        min_price = float(df["price"].min())
        max_price = float(df["price"].max())
        avg_by_city = (
            df.groupby("location")["price"].mean().round(2).to_dict()
        )
        return {
            "average_price": round(average_price, 2),
            "median_price": round(median_price, 2),
            "min_price": round(min_price, 2),
            "max_price": round(max_price, 2),
            "average_price_by_city": avg_by_city,
            "sample_size": int(df.shape[0]),
        }
