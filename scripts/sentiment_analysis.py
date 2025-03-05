import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd

class RedditSentimentAnalysis:
    def __init__(self, df, model_name="cardiffnlp/twitter-roberta-base-sentiment"):
        """
        Constructor for the sentiment analysis class.
        :param df: Pandas DataFrame containing topics and selftext.
        :param model_name: Transformer model for sentiment analysis (default: RoBERTa).
        """
        self.df = df.fillna({"selftext": ""})  # Fill NaN values with empty string
        self.model_name = model_name
        self.sentiment_model = None
        self.tokenizer = None
        self.sentiment_df = None

    def initialize_model(self):
        """
        Loads the transformer model and tokenizer for sentiment analysis.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(self.model_name)

    def analyze_sentiment(self, batch_size=16):
        """
        Performs sentiment analysis on the selftext column in batches for efficiency.
        :param batch_size: Number of samples processed in one batch.
        """
        if self.sentiment_model is None or self.tokenizer is None:
            raise ValueError("Sentiment model is not initialized. Call initialize_model() first.")

        # Store sentiment results
        sentiment_labels = []
        sentiment_scores = []

        texts = self.df["selftext"].astype(str).tolist()

        # Process in batches to speed up inference
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            inputs = self.tokenizer(batch_texts, return_tensors="pt", truncation=True, padding=True, max_length=512)

            with torch.no_grad():
                outputs = self.sentiment_model(**inputs)

            scores = torch.nn.functional.softmax(outputs.logits, dim=-1)
            sentiment_classes = torch.argmax(scores, dim=-1).tolist()

            # Convert class IDs to labels
            label_map = {0: "Negative", 1: "Neutral", 2: "Positive"}
            sentiment_labels.extend([label_map[class_id] for class_id in sentiment_classes])
            sentiment_scores.extend(scores.numpy())

        # Convert results to DataFrame
        self.sentiment_df = self.df.copy()
        self.sentiment_df["sentiment"] = sentiment_labels
        self.sentiment_df["sentiment_scores"] = sentiment_scores  # Store probability scores

    def get_sentiment_dataframe(self):
        """
        Returns the DataFrame with sentiment labels and scores.
        """
        if self.sentiment_df is None:
            raise ValueError("Sentiment DataFrame has not been created. Call analyze_sentiment() first.")
        return self.sentiment_df
