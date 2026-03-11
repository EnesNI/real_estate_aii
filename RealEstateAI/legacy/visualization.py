import pandas as pd
import matplotlib.pyplot as plt

def generate_chart():

    data = pd.read_csv("data/housing_data.csv")

    plt.figure()

    plt.scatter(data["size"], data["price"])

    plt.xlabel("Size")
    plt.ylabel("Price")

    plt.title("Price vs Size")

    plt.savefig("price_chart.png")