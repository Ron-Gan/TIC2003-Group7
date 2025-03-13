from scripts.coingecko_api_fetch import CoingeckoFetchAPI

class CoinListGenerator:
    def __init__(self):
        self.generate_coin_list()

    """
    Transform coin list from API into
    displayable format for GUI.
    """
    def generate_coin_list(self):
        self.extract_data()
        initial_list = self.response.json()
        self.coin_masterlist = []
        for coin in initial_list:
            self.coin_masterlist.append(f"{coin['id']} ({coin['symbol']})")
        return self.coin_masterlist

    # Calls CoinGecko API for list of coins
    def extract_data(self):
        try:
            self.response = CoingeckoFetchAPI(None, None, None, "coin list").retrieve_response()
        except:
            raise ValueError("List Generation Error")

    def get_list(self):
        return self.coin_masterlist