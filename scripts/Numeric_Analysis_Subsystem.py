import pandas as pd
from datetime import datetime
from tzlocal import get_localzone
from scripts.coingecko_api_fetch import CoingeckoFetchAPI
import logging

"""
NumericSubsystem should only be called to extract
historical coin data.
"""
class NumericSubsystem:
    def __init__(self, start, end, coin_name):
        self.start = datetime.timestamp(start)
        self.end = datetime.timestamp(end)
        self.coin_name = coin_name

    def get_numeric_data_df(self):
        try:
            return self.numeric_data_df
        except Exception as e:
            logging.error(f"Numeric Data DF being called before initialisation.")
            raise RuntimeError("Numeric Subsystem error") from e

    """ 
    Transforms data in dataframe, and add labels accordingly. 
    Mainly Timestamp conversion.
    """
    def transform_numbers(self):
        try:
            response = self.numeric_data_df
            df = pd.DataFrame(response['prices'])
            df = df.rename(columns={1: 'Price'})
            df = df.rename(columns={0: 'Timestamp'})
            local_tz = get_localzone()  # Detect OS timezone
            df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")  # Convert Unix timestamp
            df["Timestamp"] = df["Timestamp"].dt.tz_localize("UTC").dt.tz_convert(local_tz)
            df.insert(0,'Coin Ticker',self.coin_name)
            self.numeric_data_df = df

        except Exception as e:
            logging.error(f"Error transforming numeric DF")
            raise RuntimeError("Numeric Subsystem error") from e

    """
    Additional functions to transform data, to ease integration into Dashboard
    """
    def extract_date_time(self, df):
        try:
            df["Timestamp"] = df["Timestamp"].astype(str)
            time_col = df["Timestamp"].str.split(".").str.get(0)
            date_col = time_col.str.split(" ").str.get(0)
            time_col = time_col.str.split(" ").str.get(1)
            time_col = time_col.str.split("+").str.get(0)
            df.insert(1, "Date", date_col)
            df.insert(2, "Time", time_col)
            return df

        except Exception as e:
            logging.error(f"Error extracting date,time from timestamp")
            raise RuntimeError("Numeric Subsystem error") from e

    # Converts response into dataframe
    def convert_df(self):
        try:
            self.numeric_data_df = self.response.json()
            self.transform_numbers()
            numeric_df = self.numeric_data_df
            numeric_df.pipe(self.extract_date_time)
            self.numeric_data_df = numeric_df

        except Exception as e:
            logging.error(f"Error converting DF from CoinGecko API result")
            raise RuntimeError("The coin may not be active anymore") from e

    # Call CoingeckoAPI
    def extract_data(self):
        try:
            self.response = CoingeckoFetchAPI.for_market_data(self.start, self.end, self.coin_name).retrieve_response()

        except Exception as e:
            logging.error(f"Coingecko Input Error: {e}")
            raise RuntimeError("Coingecko Input Error.") from e