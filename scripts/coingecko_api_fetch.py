import requests
import os
from dotenv import load_dotenv

class CoingeckoFetchAPI:
    load_dotenv()

    def __init__ (self, start, end, coin_name, purpose):
        __api_key = os.getenv('COINGECKO_API_KEY')
        self.generate_url(start,end,coin_name,purpose)
        self.generate_headers(__api_key)
        self.response = requests.get(self.url, headers=self.headers)

    def retrieve_response(self):
        if self.response.status_code==200:
            print("Coingecko API fetch successful!")
            return self.response
        else:
            raise ValueError(f"Coingecko API Error: {self.response}")

    """ 
        Headers are required to parse through
        Coingecko API for DEMO API Key. Please
        update for PRO/Personal version.
    """
    def generate_headers(self, key):
        self.headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": key  # change key if necessary
        }

    """ 
        generate_url function will send a request
        for data from Coingecko API. If needed, please
        update required fields. 
    """
    def generate_url(self,start, end, coin_name, purpose):
        api_web = "https://api.coingecko.com/api"
        version = "v3"
        specifics = "coins"

        if purpose == "coin list":
            self.url = f"{api_web}/{version}/{specifics}/list"
        elif purpose == "market data":
            specifics_2 = "market_chart"
            currency = "usd"  # change currency if necessary
            precision = "2"
            self.url = f"{api_web}/{version}/{specifics}/{coin_name}/{specifics_2}/range?vs_currency={currency}&from={start}&to={end}&precision={precision}"