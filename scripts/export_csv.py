import pandas as pd
import logging

class ExportCSV:
    def __init__(self, df_text, df_num):
        self.df_text = df_text.copy()
        self.df_num = df_num.copy()

        try:
            # Extract Hour from Time
            self.df_text['Hour'] = pd.to_datetime(self.df_text['Time'], format='%H:%M:%S').dt.hour
            self.df_num['Hour'] = pd.to_datetime(self.df_num['Time'], format='%H:%M:%S').dt.hour

            # Map sentiment to numeric values
            sentiment_map = {'Positive': 1, 'Neutral': 0, 'Negative': -1}
            self.df_text['sentiment_num'] = self.df_text['sentiment'].map(sentiment_map)

            # Extract max(p_neu, p_pos, p_neg) for each row to determine the sentiment
            self.df_text['sentiment_score'] = self.df_text[['p_neg', 'p_neut', 'p_pos']].max(axis=1)

            # Compute average sentiment per hour
            self.df_text['avg_sentiment'] = self.df_text.groupby('Hour')['sentiment_num'].transform('mean')

            # Merge text and numeric data on Date
            self.df = pd.merge(self.df_text, self.df_num, on='Date', how='left')

            # Export merged dataframe to CSV
            filename = "merged_exported_data.csv"
            self.df.to_csv(filename, index=False)
            logging.info(f"Merged data exported successfully to {filename}")

        except Exception as e:
            logging.error(f"ExportCSV error: {e}")
            raise RuntimeError("Failed to process and export merged CSV.") from e
