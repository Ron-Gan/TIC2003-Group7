import os
import json
import praw
import pandas as pd
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
import prawcore.exceptions 

class RedditAPI:
    def __init__(self, subreddit: str, coin_tinker: list, start_datetime: datetime, end_datetime: datetime):
        """
        Initialize the RedditAPI class with subreddit, coin keywords, and datetime range.
        """
        self.subreddit_name = subreddit
        self.coin_tinker = coin_tinker
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.reddit = self.create_reddit_instance()
        self.subreddit = self.reddit.subreddit(self.subreddit_name)

    def create_reddit_instance(self):
        """Creates and authenticates a Reddit instance using environment variables."""
        load_dotenv()  # Load credentials from .env file

        reddit = praw.Reddit(
            client_id=os.getenv('CLIENT_ID'),
            client_secret=os.getenv('CLIENT_SECRET'),
            user_agent=os.getenv('USER_AGENT'),
            username=os.getenv('USERN'),  
            password=os.getenv('PASSWORD')
        )
        return reddit

    def search_subreddit(self):
        """
        Search the subreddit for posts related to the given coin_tinker keywords
        within the specified start_datetime and end_datetime range.
        """
        search_results = []
        start_timestamp = self.start_datetime.timestamp()
        end_timestamp = self.end_datetime.timestamp()

        if not self.coin_tinker or all(not keyword.strip() for keyword in self.coin_tinker):
            print("Error: No valid keywords provided.")
            return pd.DataFrame()

        for keyword in self.coin_tinker:
            try:
                # Ensure keyword is valid
                if not isinstance(keyword, str) or len(keyword.strip()) == 0:
                    print(f"Skipping invalid keyword: {keyword}")
                    continue

                print(f"Searching for keyword: {keyword} in r/{self.subreddit_name}")

                # Fetch posts with retries in case of API failure
                retry_attempts = 3
                for attempt in range(retry_attempts):
                    try:
                        posts = list(self.subreddit.search(query=keyword, limit=100))  # Fetch posts
                        if not posts:
                            print(f"No results for '{keyword}' in r/{self.subreddit_name}.")
                        break  # Exit retry loop if successful
                    except prawcore.exceptions.RequestException as e:
                        print(f"API request failed (Attempt {attempt+1}/{retry_attempts}): {e}")
                        time.sleep(10)  # Wait before retrying
                    except prawcore.exceptions.TooManyRequests as e:
                        print(f"Rate limit exceeded. Waiting before retrying: {e}")
                        time.sleep(30)  # Wait longer if rate-limited
                    except Exception as e:
                        print(f"Unexpected error: {e}")
                        break  # Stop retrying on unknown errors

                for post in posts:
                    post_timestamp = post.created_utc  # Use correct timestamp field

                    # Filter posts based on the selected time range
                    if start_timestamp <= post_timestamp <= end_timestamp:
                        search_results.append({
                            'id': post.id,
                            'title': post.title,
                            'selftext': getattr(post, 'selftext', ''),  # Handle missing text
                            'created': datetime.fromtimestamp(post_timestamp, tz=timezone.utc),
                            'upvote_ratio': getattr(post, 'upvote_ratio', 0),
                            'ups': getattr(post, 'ups', 0),
                            'downs': getattr(post, 'downs', 0),
                            'score': getattr(post, 'score', 0),
                        })

            except Exception as e:
                print(f"Error searching subreddit for keyword '{keyword}': {e}")

        return pd.DataFrame(search_results) if search_results else pd.DataFrame(columns=[
            'id', 'title', 'selftext', 'created', 'upvote_ratio', 'ups', 'downs', 'score'
        ])
