import requests
import os
from dotenv import load_dotenv
import logging

class CoingeckoFetchAPI:
    load_dotenv()

    def __init__ (self, url):
        self.api_key = os.getenv('COINGECKO_API_KEY')
        self.url = url
        self.headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": self.api_key
        }
        try:
            self.response = requests.get(self.url, headers=self.headers)
        except requests.exceptions.ConnectionError:
            logging.error("No internet connection detected.")
            raise RuntimeError("No internet connection. Please connect and restart.")


    def retrieve_response(self):
        if self.response.status_code == 200:
            logging.info("Coingecko API fetch successful!")
            return self.response
        else:
            raise ValueError(f"Please check your ticker input {self.response}")

    #Factory Methods
    @classmethod
    def for_coin_list(cls):
        url = "https://api.coingecko.com/api/v3/coins/list"
        return cls(url)

    @classmethod
    def for_market_data(cls, start, end, coin_name, currency="usd", precision="2"):
        url = (
            f"https://api.coingecko.com/api/v3/coins/{coin_name}/market_chart/range"
            f"?vs_currency={currency}&from={start}&to={end}&precision={precision}"
        )
        return cls(url)