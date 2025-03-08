import pandas as pd

class ExportCSV:
    def __init__(self, dataframe: pd.DataFrame):

        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame.")
        self.dataframe = dataframe

    def to_csv(self, filename: str = "exported_data.csv") -> str:

        self.dataframe.to_csv(filename, index=False)
        return filename
