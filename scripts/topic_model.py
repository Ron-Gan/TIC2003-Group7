import pandas as pd
from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN
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
        Dynamically initializes BERTopic with optimized parameters for small and large datasets.
        """
        embedding_model = SentenceTransformer(self.model_name)
        dataset_size = len(self.df)

        if dataset_size < 10:  
            print("🔹 Using small dataset optimization")
            umap_model = UMAP(n_components=2, n_neighbors=2, min_dist=0.1, metric="cosine")
            hdbscan_model = HDBSCAN(min_cluster_size=2, min_samples=1)
        else:  
            print("🔹 Using large dataset optimization")
            umap_model = UMAP(n_components=5, n_neighbors=15, min_dist=0.1, metric="cosine")
            hdbscan_model = HDBSCAN(min_cluster_size=5, min_samples=5)

        
        self.topic_model = BERTopic(
            embedding_model=embedding_model,
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            nr_topics="auto"
        )

    def fit_transform(self):
        """
        Fits the topic model on the selftext column and generates topic assignments.
        """
        if self.topic_model is None:
            raise ValueError("Topic model is not initialized. Call initialize_model() first.")
        
        dataset_size = len(self.df)
        if dataset_size == 0:
            raise ValueError("Dataframe is empty. Ensure you have retrieved valid Reddit posts.")
        
        print(f"🔹 Running BERTopic on {dataset_size} Reddit posts...")

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
