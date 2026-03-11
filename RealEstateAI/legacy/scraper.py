import requests
from bs4 import BeautifulSoup

def scrape_example():

    url = "https://example.com"

    r = requests.get(url)

    soup = BeautifulSoup(r.text, "html.parser")

    titles = []

    for h in soup.find_all("h1"):  # loop
        titles.append(h.text)

    return titles