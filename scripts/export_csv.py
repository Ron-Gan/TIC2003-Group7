import pandas as pd
from scripts.Numeric_Analysis_Subsystem import NumericSubsystem
from scripts.sentiment_analysis import RedditSentimentAnalysis

"""
    Takes in an input, checks which class it belongs to,
    and calls the conversion methods for each class
    to convert to dataframe, and export to CSV
"""
class ExportCSV:
    def __init__(self,input):
        self.input = input

        if not isinstance(self.input, (RedditSentimentAnalysis, NumericSubsystem)):
            raise ValueError(f"{self.input} is an invalid type to export CSV.")
        if type(self.input)==NumericSubsystem:
            self.input.convert_df()
            self.df = self.input.get_numeric_data_df()
            self.type_result = "Number"
        else:
            self.df = self.input.get_sentiment_dataframe()
            self.type_result = "Text"

        filename = f"{self.type_result}_exported_data.csv"
        self.df.to_csv(filename, index=False)
        print("Generated: ",filename)
