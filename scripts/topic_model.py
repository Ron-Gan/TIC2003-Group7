import pandas as pd
from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
import logging


class RedditTopicModel:
    def __init__(self, df, model_name="all-MiniLM-L6-v2"):
        self.df = df.fillna({"comments": ""})  # Fill NaN comments with empty string
        self.model_name = model_name
        self.topic_model = None
        self.topics = None
        self.probs = None
        self.topic_df = None
        self.filtered_topic_df = None

    def initialize_model(self):
        embedding_model = SentenceTransformer(self.model_name)
        dataset_size = len(self.df)

        if dataset_size < 10:
            logging.info("Using small dataset optimisation for topic modelling")
            umap_model = UMAP(n_components=2, n_neighbors=2, min_dist=0.1, metric="cosine")
            hdbscan_model = HDBSCAN(min_cluster_size=2, min_samples=1)
        else:
            logging.info("Using large dataset optimisation for topic modelling")
            umap_model = UMAP(n_components=5, n_neighbors=15, min_dist=0.1, metric="cosine")
            hdbscan_model = HDBSCAN(min_cluster_size=5, min_samples=5)

        self.topic_model = BERTopic(
            embedding_model=embedding_model,
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            nr_topics="auto"
        )

    def fit_transform(self):
        if self.topic_model is None:
            logging.error("Topic model is not initialized. Call initialize_model() first")
            raise ValueError("Topic model is not initialized.")

        if self.df.empty:
            logging.error("Dataframe is empty for topic modelling.")
            raise ValueError("Dataframe is empty. Ensure you have Reddit posts.")

        logging.info(f"\nRunning BERTopic on {len(self.df)} Reddit post comments...")

        comment_texts = self.df["comments"].apply(lambda x: " ".join(x) if isinstance(x, list) else str(x))
        self.topics, self.probs = self.topic_model.fit_transform(comment_texts)

    def process_topics(self, top_n=5):
        if self.topics is None:
            logging.error("Topics have not been generated. Call fit_transform() first.")
            raise ValueError("Topic modelling error. Please try again")

        self.topic_df = self.df.copy()
        self.topic_df["topic"] = self.topics

        self.topic_df = self.topic_df[[
            "id", "title", "created", "upvote_ratio", "ups", "downs", "score", "comments", "topic"
        ]]

        self.filtered_topic_df = self.topic_df[self.topic_df['topic'] != -1].reset_index(drop=True)
        logging.info(f"\n Filtered dataset size: {len(self.filtered_topic_df)} (Outliers removed)")

        if self.topic_model is None:
            logging.error("BERTopic model not initialized. Cannot summarize topics.")
            raise ValueError("BERTopic model not initialized. Please try again.")

        topic_info = self.topic_model.get_topic_info()

    def get_topic_dataframe(self):
        if self.filtered_topic_df is None:
            logging.error("Filtered topic DataFrame has not been created. Call process_topics() first.")
            raise ValueError("Topic modelling error. Please try again.")
        return self.filtered_topic_df

    def save_model(self, save_path="bertopic_model"):
        if self.topic_model is None:
            logging.error("Topic model is not initialized. Call initialize_model() first.")
            raise ValueError("Topic modelling error. Please try again.")
        self.topic_model.save(save_path)

    def load_model(self, load_path="bertopic_model"):
        self.topic_model = BERTopic.load(load_path)