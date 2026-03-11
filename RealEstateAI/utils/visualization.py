from __future__ import annotations

from typing import Iterable
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px


def price_vs_square_feet_plot(df: pd.DataFrame):
    """Interactive scatter plot of price vs size."""

    fig = px.scatter(
        df,
        x="size",
        y="price",
        color="location",
        title="Price vs Square Feet",
        labels={"size": "Square Feet", "price": "Price"},
    )
    fig.update_traces(marker=dict(size=10, opacity=0.7))
    return fig


def average_price_by_city_plot(df: pd.DataFrame):
    """Interactive bar chart of average price by city."""

    summary = df.groupby("location", as_index=False)["price"].mean()
    summary = summary.sort_values("price", ascending=False)
    fig = px.bar(
        summary,
        x="location",
        y="price",
        title="Average Price by City",
        labels={"location": "City", "price": "Average Price"},
    )
    return fig


def price_trend_plot(df: pd.DataFrame):
    """Interactive line chart showing price trend by year built."""

    trend = df.groupby("year_built", as_index=False)["price"].mean()
    trend = trend.sort_values("year_built")
    fig = px.line(
        trend,
        x="year_built",
        y="price",
        title="Average Price by Year Built",
        labels={"year_built": "Year Built", "price": "Average Price"},
    )
    return fig


def price_distribution_plot(df: pd.DataFrame):
    """Matplotlib histogram for price distribution."""

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(df["price"], bins=15, color="#4C78A8", alpha=0.8)
    ax.set_title("Price Distribution")
    ax.set_xlabel("Price")
    ax.set_ylabel("Count")
    ax.grid(True, linestyle="--", alpha=0.4)
    return fig


def predicted_vs_actual_plot(actual: Iterable[float], predicted: Iterable[float]):
    """Matplotlib scatter plot of predicted vs actual prices."""

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(actual, predicted, color="#F58518", alpha=0.7)
    ax.set_title("Predicted vs Actual Prices")
    ax.set_xlabel("Actual Price")
    ax.set_ylabel("Predicted Price")
    ax.grid(True, linestyle="--", alpha=0.4)
    return fig
