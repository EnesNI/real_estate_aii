from __future__ import annotations

from typing import Any, Optional

import pandas as pd
import requests
import streamlit as st

from core.config import get_settings
from ml.model import PredictionEngine
from utils.data_processing import load_housing_data
from utils.visualization import (
    average_price_by_city_plot,
    predicted_vs_actual_plot,
    price_distribution_plot,
    price_trend_plot,
    price_vs_square_feet_plot,
)

settings = get_settings()

st.set_page_config(page_title="RealEstate Predict", layout="wide")


@st.cache_data
def load_dataset() -> pd.DataFrame:
    """Load the housing dataset for analytics."""

    return load_housing_data(settings.data_dir / "housing_data.csv")


def _extract_error(response: requests.Response) -> str:
    """Extract error details from an API response."""

    try:
        payload = response.json()
        if isinstance(payload, dict) and "detail" in payload:
            return str(payload["detail"])
    except ValueError:
        pass
    return response.text


def api_get(endpoint: str, params: Optional[dict[str, Any]] = None, token: Optional[str] = None) -> Any:
    """Issue a GET request to the API."""

    url = f"{settings.api_base_url}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
    except requests.RequestException as exc:
        raise RuntimeError(
            "API unavailable. Start the backend with `uvicorn api.main:app --reload`."
        ) from exc
    if response.status_code >= 400:
        raise RuntimeError(_extract_error(response))
    return response.json()


def api_post(endpoint: str, payload: Optional[dict[str, Any]] = None, token: Optional[str] = None) -> Any:
    """Issue a POST request to the API."""

    url = f"{settings.api_base_url}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
    except requests.RequestException as exc:
        raise RuntimeError(
            "API unavailable. Start the backend with `uvicorn api.main:app --reload`."
        ) from exc
    if response.status_code >= 400:
        raise RuntimeError(_extract_error(response))
    return response.json()


if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

st.sidebar.title("RealEstate Predict")

if st.session_state.token is None:
    auth_mode = st.sidebar.radio("Access", ["Login", "Register"], horizontal=True)

    if auth_mode == "Login":
        with st.sidebar.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
        if submitted:
            try:
                result = api_post("/login", {"username": username, "password": password})
                st.session_state.token = result["token"]
                st.session_state.user = result["user"]
                st.rerun()
            except RuntimeError as exc:
                st.sidebar.error(str(exc))
    else:
        with st.sidebar.form("register_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Register")
        if submitted:
            try:
                api_post("/register", {"username": username, "email": email, "password": password})
                st.sidebar.success("Registration successful. Please log in.")
            except RuntimeError as exc:
                st.sidebar.error(str(exc))
else:
    user = st.session_state.user
    st.sidebar.success(f"Logged in as {user['username']}")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Property Search", "Prediction Tool", "Market Analytics", "User Profile"],
)


if page == "Dashboard":
    st.title("Real Estate Analytics Dashboard")
    st.write("Overview of market performance and dataset insights.")

    try:
        trends = api_get("/market-trends")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Average Price", f"${trends['average_price']:,.0f}")
        col2.metric("Median Price", f"${trends['median_price']:,.0f}")
        col3.metric("Min Price", f"${trends['min_price']:,.0f}")
        col4.metric("Max Price", f"${trends['max_price']:,.0f}")
    except RuntimeError as exc:
        st.error(f"Unable to load market trends: {exc}")

    df = load_dataset()
    st.plotly_chart(average_price_by_city_plot(df), use_container_width=True)


if page == "Property Search":
    st.title("Property Search")
    st.write("Filter and explore available properties.")

    col1, col2, col3, col4 = st.columns(4)
    city = col1.text_input("City")
    state = col2.text_input("State (2-letter)")
    min_price = col3.number_input("Min Price", min_value=0, step=10000, value=0)
    max_price = col4.number_input("Max Price", min_value=0, step=10000, value=0)

    col5, col6, col7, col8 = st.columns(4)
    min_sqft = col5.number_input("Min Sq Ft", min_value=0, step=10, value=0)
    max_sqft = col6.number_input("Max Sq Ft", min_value=0, step=10, value=0)
    bedrooms = col7.number_input("Bedrooms", min_value=0, step=1, value=0)
    bathrooms = col8.number_input("Bathrooms", min_value=0.0, step=0.5, value=0.0)

    if st.button("Search Properties"):
        params = {
            "city": city or None,
            "state": state or None,
            "min_price": min_price or None,
            "max_price": max_price or None,
            "min_sqft": min_sqft or None,
            "max_sqft": max_sqft or None,
            "bedrooms": bedrooms or None,
            "bathrooms": bathrooms or None,
        }
        try:
            results = api_get("/properties", params=params)
            if results:
                st.dataframe(results, use_container_width=True)
            else:
                st.info("No properties matched your filters.")
        except RuntimeError as exc:
            st.error(f"Search failed: {exc}")

    if st.button("Scrape Sample Listings"):
        try:
            response = api_post("/scrape", {})
            st.success(f"Added {response['added']} new listings from scraping.")
        except RuntimeError as exc:
            st.error(f"Scraping failed: {exc}")

    if city:
        try:
            amenity_data = api_get("/amenities", params={"city": city})
            st.subheader("Nearby Amenities")
            st.write(", ".join(amenity_data["amenities"]))
        except RuntimeError as exc:
            st.warning(f"Amenities unavailable: {exc}")


if page == "Prediction Tool":
    st.title("Price Prediction Tool")
    st.write("Generate property price predictions using the ML model.")

    if st.session_state.token is None:
        st.info("Please log in to create predictions.")
    else:
        with st.form("prediction_form"):
            location = st.text_input("Location (City)")
            square_feet = st.number_input("Square Feet", min_value=10.0, step=10.0, value=70.0)
            bedrooms = st.number_input("Bedrooms", min_value=0, step=1, value=2)
            bathrooms = st.number_input("Bathrooms", min_value=0.0, step=0.5, value=1.0)
            year_built = st.number_input("Year Built", min_value=1800, max_value=2100, value=2010)
            submitted = st.form_submit_button("Predict")

        if submitted:
            payload = {
                "location": location,
                "square_feet": square_feet,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "year_built": year_built,
            }
            try:
                result = api_post("/predict", payload, token=st.session_state.token)
                st.success("Prediction completed.")
                col1, col2 = st.columns(2)
                col1.metric("Predicted Price", f"${result['predicted_price']:,.0f}")
                col2.metric("5-Year Projection", f"${result['future_price']:,.0f}")
            except RuntimeError as exc:
                st.error(f"Prediction failed: {exc}")


if page == "Market Analytics":
    st.title("Market Analytics")
    df = load_dataset()

    st.plotly_chart(price_vs_square_feet_plot(df), use_container_width=True)
    st.plotly_chart(price_trend_plot(df), use_container_width=True)

    st.subheader("Price Distribution")
    st.pyplot(price_distribution_plot(df))

    st.subheader("Predicted vs Actual")
    engine = PredictionEngine()
    engine.ensure_model()
    predictions = engine.predict_batch(df.drop(columns=["price"]))
    st.pyplot(predicted_vs_actual_plot(df["price"], predictions))


if page == "User Profile":
    st.title("User Profile")

    if st.session_state.token is None:
        st.info("Please log in to view your profile and prediction history.")
    else:
        try:
            profile = api_get("/profile", token=st.session_state.token)
            st.subheader("Account Details")
            st.write(profile["user"])
            st.metric("Prediction Count", profile["prediction_count"])
        except RuntimeError as exc:
            st.error(f"Profile load failed: {exc}")

        try:
            history = api_get("/predictions", token=st.session_state.token)
            st.subheader("Prediction History")
            if history:
                st.dataframe(history, use_container_width=True)
            else:
                st.info("No predictions yet.")
        except RuntimeError as exc:
            st.error(f"Prediction history unavailable: {exc}")
