import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

class RealEstateModel:

    def __init__(self):
        self.model = None

    def train(self):

        data = pd.read_csv("data/housing_data.csv")

        X = data.drop("price", axis=1)
        y = data["price"]

        pre = ColumnTransformer([
            ("location", OneHotEncoder(), ["location"]),
            ("num", "passthrough",
             ["size", "bedrooms", "bathrooms", "year_built"])
        ])

        reg = RandomForestRegressor(n_estimators=200)

        pipeline = Pipeline([
            ("pre", pre),
            ("reg", reg)
        ])

        pipeline.fit(X, y)

        self.model = pipeline

        with open("model.pkl", "wb") as f:
            pickle.dump(pipeline, f)

    def load(self):
        with open("model.pkl", "rb") as f:
            self.model = pickle.load(f)

    def predict(self, data):

        df = pd.DataFrame([data])

        result = self.model.predict(df)[0]

        return round(result, 2)

    def future_price(self, price):

        growth = 0.04
        years = 5

        for i in range(years):  # loop requirement
            price = price * (1 + growth)

        return round(price, 2)