import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd

class RedditSentimentAnalysis:
    def __init__(self, df, model_name="cardiffnlp/twitter-roberta-base-sentiment"):
        """
        Constructor for the sentiment analysis class.
        :param df: Pandas DataFrame containing topics and comments.
        :param model_name: Transformer model for sentiment analysis (default: RoBERTa).
        """
        self.df = df.fillna({"comments": ""})  # Fill NaN values with empty string
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
        Performs sentiment analysis on the comments column in batches for efficiency.
        :param batch_size: Number of samples processed in one batch.
        """
        if self.sentiment_model is None or self.tokenizer is None:
            raise ValueError("Sentiment model is not initialized. Call initialize_model() first.")

        # Store sentiment results
        sentiment_labels = []
        p_neg_list = []
        p_neut_list = []
        p_pos_list = []

        texts = self.df["comments"].apply(lambda x: " ".join(x) if isinstance(x, list) else str(x)).astype(str).tolist()

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

            # Extract individual probabilities
            p_neg_list.extend(scores[:, 0].tolist())
            p_neut_list.extend(scores[:, 1].tolist())
            p_pos_list.extend(scores[:, 2].tolist())

        # Store intermediate results
        self.df["sentiment"] = sentiment_labels
        self.df["p_neg"] = p_neg_list
        self.df["p_neut"] = p_neut_list
        self.df["p_pos"] = p_pos_list

    def finalize_sentiment_dataframe(self):
        """
        Formats and returns the final DataFrame with required columns and date/time split.
        """
        if "sentiment" not in self.df.columns or "p_neg" not in self.df.columns:
            raise ValueError("Sentiment analysis has not been run. Call analyze_sentiment() first.")

        self.df["date"] = pd.to_datetime(self.df["created"]).dt.date.astype(str)
        self.df["time"] = pd.to_datetime(self.df["created"]).dt.time.astype(str)

        self.sentiment_df = self.df[[
            "id", "title", "created", "date", "time", "upvote_ratio", "ups", "downs", "score",
            "comments", "topic", "sentiment", "p_neg", "p_neut", "p_pos"
        ]].copy()

    def get_sentiment_dataframe(self):
        """
        Returns the finalized DataFrame with sentiment labels and probability scores.
        """
        if self.sentiment_df is None:
            raise ValueError("Sentiment DataFrame has not been finalized. Call finalize_sentiment_dataframe() first.")
        return self.sentiment_df