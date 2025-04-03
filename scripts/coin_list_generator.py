from scripts.coingecko_api_fetch import CoingeckoFetchAPI
import logging
import requests  # To check for connectivity issues

class CoinListGenerator:
    def __init__(self):
        self.coin_masterlist = []  # Ensure this exists even if an error occurs
        try:
            self.generate_coin_list()
        except RuntimeError as e:
            logging.error(f"CoinListGenerator Error: {e}")
            raise

    """
    Transform coin list from API into displayable format for GUI.
    """
    def generate_coin_list(self):
        try:
            self.extract_data()
            initial_list = self.response.json()
            self.coin_masterlist = [f"{coin['id']} ({coin['symbol']})" for coin in initial_list]

            if not self.coin_masterlist:
                raise RuntimeError("Coingecko API error.")

        except requests.exceptions.ConnectionError:
            logging.error("No internet connection detected.")
            raise RuntimeError("No internet connection. Please connect and restart.")

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise RuntimeError("Failed to generate coin list. Check your internet or API.") from e

    # Calls CoinGecko API for list of coins
    def extract_data(self):
        self.response = CoingeckoFetchAPI(None, None, None, "coin list").retrieve_response()

    def get_list(self):
        return self.coin_masterlist
