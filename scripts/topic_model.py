import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

class RedditTopicModel:
    def __init__(self, df, model_name="all-MiniLM-L6-v2"):
        """
        Constructor to initialize the topic modeling class.
        :param df: Pandas DataFrame containing Reddit posts.
        :param model_name: SentenceTransformer model name (default: "all-MiniLM-L6-v2").
        """
        self.df = df.fillna({"selftext": ""})  # Fill NaN with empty string
        self.model_name = model_name
        self.topic_model = None
        self.topics = None
        self.probs = None
        self.topic_df = None

    def initialize_model(self):
        """
        Initializes BERTopic with an embedding model suitable for social media text.
        """
        embedding_model = SentenceTransformer(self.model_name)
        self.topic_model = BERTopic(embedding_model=embedding_model)

    def fit_transform(self):
        """
        Fits the topic model on the selftext column and generates topic assignments.
        """
        if self.topic_model is None:
            raise ValueError("Topic model is not initialized. Call initialize_model() first.")
        
        # Transforming the selftext column
        self.topics, self.probs = self.topic_model.fit_transform(self.df["selftext"].astype(str))

    def create_topic_dataframe(self):
        """
        Creates a DataFrame containing the topics and corresponding selftext.
        """
        if self.topics is None:
            raise ValueError("Topics have not been generated. Call fit_transform() first.")
        
        self.topic_df = pd.DataFrame({"topic": self.topics, "selftext": self.df["selftext"]})

    def get_topic_dataframe(self):
        """
        Returns the topic DataFrame.
        """
        if self.topic_df is None:
            raise ValueError("Topic DataFrame has not been created. Call create_topic_dataframe() first.")
        return self.topic_df

    def save_model(self, save_path="bertopic_model"):
        """
        Saves the BERTopic model for later use.
        :param save_path: Directory where the model should be saved.
        """
        if self.topic_model is None:
            raise ValueError("Topic model is not initialized. Call initialize_model() first.")
        self.topic_model.save(save_path)
        print(f"Model saved to {save_path}")

    def load_model(self, load_path="bertopic_model"):
        """
        Loads a previously saved BERTopic model.
        :param load_path: Directory where the model is stored.
        """
        self.topic_model = BERTopic.load(load_path)
        print(f"Model loaded from {load_path}")
