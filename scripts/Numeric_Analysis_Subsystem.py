import pandas as pd
from datetime import datetime
from tzlocal import get_localzone
import math
from scripts.coingecko_api_fetch import CoingeckoFetchAPI

"""
NumericSubsystem should only be called to extract
historical coin data.
"""
class NumericSubsystem:
    def __init__(self, start, end, coin_name, purpose):
        self.start = datetime.timestamp(start)
        self.end = datetime.timestamp(end)
        self.coin_name = coin_name
        self.purpose = purpose

    def get_numeric_data_df(self):
        return self.numeric_data_df

    """ 
    Transforms data in dataframe, and add labels accordingly. 
    Mainly Timestamp conversion.
    """
    def transform_numbers(self):
        response = self.numeric_data_df
        df = pd.DataFrame(response['prices'])
        df = df.rename(columns={1: 'Price'})
        df = df.rename(columns={0: 'Timestamp'})
        local_tz = get_localzone()  # Detect OS timezone
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")  # Convert Unix timestamp
        df["Timestamp"] = df["Timestamp"].dt.tz_localize("UTC").dt.tz_convert(local_tz)
        self.numeric_data_df = df

    # Converts response into dataframe
    def convert_df(self):
        self.numeric_data_df = self.response.json()
        self.transform_numbers()
        print(self.numeric_data_df)

    # Call CoingeckoAPI
    def extract_data(self):
        try:
            self.response = CoingeckoFetchAPI(self.start, self.end, self.coin_name, self.purpose).retrieve_response()
        except:
            raise ValueError("Input Error")