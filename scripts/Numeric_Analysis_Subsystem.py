import pandas as pd
from scripts.coingecko_api_fetch import FetchNumericData

def transform_numbers(response):
    df = pd.DataFrame(response.json()['prices'])
    df = df.drop([0],axis=1)
    return df

""" Determine Intervals used to determine time between
    each row in the output.
    Returns intervals in minutes """
def determine_interval(start,end):
    difference = end-start
    if difference < 86400:
        intervals = 5
    elif 86400 < difference < 7776000:
        intervals = 60
    else:
        intervals = 24*60
    return intervals

class NumericAnalysis:
    def __new__(cls, start, end, coin_name, purpose):
        try:
            numeric_data = FetchNumericData(start, end, coin_name, purpose)
            numeric_data = transform_numbers(numeric_data)
            print(numeric_data)
        except:
            raise Exception("Input Error")