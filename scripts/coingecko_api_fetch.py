import requests
import os
from datetime import datetime
from dotenv import load_dotenv
import math

def convert_to_unix(date_input):
    unix_timestamp = math.trunc(datetime.timestamp(date_input))
    return unix_timestamp

""" generate_url function will send a request
    for data from Coingecko API. If needed, please
    update required fields. """
def generate_url(start,end,coin_name, purpose):
    api_web = "https://api.coingecko.com/api"
    version = "v3"
    specifics = "coins"

    if purpose == "coin list":
        url = f"{api_web}/{version}/{specifics}/list"
    elif purpose=="market data":
        specifics_2 = "market_chart"
        currency = "usd" #change currency if necessary
        precision = "2"
        url = f"{api_web}/{version}/{specifics}/{coin_name}/{specifics_2}/range?vs_currency={currency}&from={start}&to={end}&precision={precision}"
    return url

""" Headers are required to parse through
    Coingecko API for DEMO API Key. Please
    update for PRO/Personal version."""
def generate_headers(demo_key):
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": demo_key  # change key if necessary
    }
    return headers

class FetchNumericData:
    load_dotenv()
    __api_key = os.getenv('COINGECKO_API_KEY')

    def __new__ (cls, start, end, coin_name, purpose):
        start = convert_to_unix(start)
        end = convert_to_unix(end)
        url = generate_url(start,end,coin_name,purpose)
        headers = generate_headers(cls.__api_key)
        response = requests.get(url, headers=headers)

        if response.status_code==200:
            print(response)
            return response
        else:
            raise Exception(f"Coingecko API Error: {response}")