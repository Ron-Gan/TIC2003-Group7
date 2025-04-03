import os
import praw
import pandas as pd
import time
import logging
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import prawcore

# Setup logging
logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class RedditAPI:
    def __init__(self, subreddit: str, coin_ticker: list, start_datetime: datetime, end_datetime: datetime):
        self.subreddit_name = subreddit
        self.coin_ticker = coin_ticker
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.reddit = self.create_reddit_instance()
        self.subreddit = self.reddit.subreddit(self.subreddit_name)

    def create_reddit_instance(self):
        """Creates and authenticates a Reddit instance using environment variables."""
        load_dotenv()
        try:
            reddit = praw.Reddit(
                client_id=os.getenv('CLIENT_ID'),
                client_secret=os.getenv('CLIENT_SECRET'),
                user_agent=os.getenv('USER_AGENT'),
                username=os.getenv('USERN'),
                password=os.getenv('PASSWORD')
            )
            logging.info("Reddit API authenticated successfully.")
            return reddit
        except Exception as e:
            logging.error(f"Failed to authenticate Reddit API: {e}")
            raise RuntimeError("Failed to authenticate Reddit API.") from e

    def search_subreddit(self):
        """Retrieve posts from the subreddit and filter them based on keywords and time range."""
        search_results = []
        start_timestamp = self.start_datetime.timestamp()
        end_timestamp = self.end_datetime.timestamp()

        if not self.coin_ticker or all(not keyword.strip() for keyword in self.coin_ticker):
            logging.error("No valid keywords provided.")
            raise ValueError("No valid keywords provided.")

        for keyword in self.coin_ticker:
            posts = []

            try:
                if not isinstance(keyword, str) or len(keyword.strip()) == 0:
                    logging.warning(f"Skipping invalid keyword: {keyword}")
                    continue

                logging.info(f"Fetching latest posts in r/{self.subreddit_name} for keyword: {keyword}")

                retry_attempts = 3
                for attempt in range(retry_attempts):
                    try:
                        posts = list(self.subreddit.new(limit=1000))
                        if not posts:
                            logging.warning(f"No results for '{keyword}' in r/{self.subreddit_name}.")
                        break
                    except prawcore.exceptions.BadRequest:
                        logging.error(f"Bad request error for subreddit '{self.subreddit_name}'.")
                        raise RuntimeError(f"Bad request error for subreddit '{self.subreddit_name}'.")  # ✅ Raise
                    except prawcore.exceptions.RequestException as e:
                        logging.error(f"API request failed (Attempt {attempt+1}/{retry_attempts}): {e}")
                        time.sleep(10)
                    except prawcore.exceptions.TooManyRequests as e:
                        logging.error(f"Rate limit exceeded. Waiting: {e}")
                        time.sleep(30)
                    except Exception as e:
                        logging.error(f"Unexpected error: {e}")
                        raise RuntimeError(f"Please try another subreddit")

                for post in posts:
                    post_timestamp = post.created_utc

                    if start_timestamp <= post_timestamp <= end_timestamp and keyword.lower() in post.title.lower():
                        try:
                            post.comments.replace_more(limit=0)
                            top_comments = [comment.body for comment in post.comments[:5]]
                        except Exception as e:
                            logging.error(f"Failed to fetch comments for post {post.id}: {e}")
                            raise RuntimeError(f"Failed to fetch comments for post {post.id}: {e}")

                        search_results.append({
                            'id': post.id,
                            'title': post.title,
                            'selftext': getattr(post, 'selftext', ''),
                            'created': datetime.fromtimestamp(post_timestamp, tz=timezone.utc).astimezone(timezone(timedelta(hours=8))),
                            'upvote_ratio': getattr(post, 'upvote_ratio', 0),
                            'ups': getattr(post, 'ups', 0),
                            'downs': getattr(post, 'downs', 0),
                            'score': getattr(post, 'score', 0),
                            'comments': top_comments
                        })

            except Exception as e:
                logging.error(f"Error searching subreddit for keyword '{keyword}': {e}")
                raise

        df = pd.DataFrame(search_results)
        if df.empty:
            logging.error("No reddit posts matched the given criteria.")
            raise RuntimeError("No reddit posts matched the given criteria.")

        return df
