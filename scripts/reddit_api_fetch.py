import os
import praw
import pandas as pd
import time
from datetime import datetime, timezone, date, time
from dotenv import load_dotenv
import prawcore
from praw.models import MoreComments
import prawcore.exceptions  

class RedditAPI:
    def __init__(self, subreddit: str, coin_tinker: list, start_datetime: datetime, end_datetime: datetime):
        """
        Initialize the RedditAPI class with subreddit, coin keywords, and datetime range.
        """
        self.subreddit_name = subreddit
        self.coin_ticker = coin_tinker
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
        Retrieve posts from the subreddit within the specified start_datetime and end_datetime range.
        Extracts relevant post data and top-level comments (up to 5 per post).
        """
        search_results = []
        start_timestamp = self.start_datetime.timestamp()
        end_timestamp = self.end_datetime.timestamp()

        if not self.coin_ticker or all(not keyword.strip() for keyword in self.coin_ticker):
            print("Error: No valid keywords provided.")
            return pd.DataFrame()

        for keyword in self.coin_ticker:
            posts = []  # Initialize posts to avoid undefined variable error

            try:
                # Ensure keyword is valid
                if not isinstance(keyword, str) or len(keyword.strip()) == 0:
                    print(f"Skipping invalid keyword: {keyword}")
                    continue

                print(f"Fetching latest posts in r/{self.subreddit_name} and filtering by keyword: {keyword}")

                # Fetch latest posts instead of using `.search()`
                retry_attempts = 3
                for attempt in range(retry_attempts):
                    try:
                        posts = list(self.subreddit.new(limit=1000))  # Fetch latest posts
                        # print(f"Found {len(posts)} posts in r/{self.subreddit_name}")
                        if not posts:
                            print(f"No results for '{keyword}' in r/{self.subreddit_name}.")
                        break  # Exit retry loop if successful
                    except prawcore.exceptions.BadRequest:
                        print(f"Bad request error for subreddit '{self.subreddit_name}'. Skipping.")
                        posts = []
                        break
                    except prawcore.exceptions.RequestException as e:
                        print(f"API request failed (Attempt {attempt+1}/{retry_attempts}): {e}")
                        time.sleep(10)  # Wait before retrying
                    except prawcore.exceptions.TooManyRequests as e:
                        print(f"Rate limit exceeded. Waiting before retrying: {e}")
                        time.sleep(30)  # Wait longer if rate-limited
                    except Exception as e:
                        print(f"Unexpected error: {e}")
                        posts = []
                        break

                for post in posts:
                    post_timestamp = post.created_utc  

                    # Filter posts based on time range and keyword presence
                    if start_timestamp <= post_timestamp <= end_timestamp and keyword.lower() in post.title.lower():
                        # Extract comments
                        try:
                            post.comments.replace_more(limit=0)  # Remove MoreComments
                            top_comments = [comment.body for comment in post.comments[:5]]  # Top 5 comments
                        except Exception as e:
                            print(f"Failed to fetch comments for post {post.id}: {e}")
                            top_comments = []

                        search_results.append({
                            'id': post.id,
                            'title': post.title,
                            'selftext': getattr(post, 'selftext', ''),  # Handle missing text
                            'created': datetime.fromtimestamp(post_timestamp, tz=timezone.utc),
                            'upvote_ratio': getattr(post, 'upvote_ratio', 0),
                            'ups': getattr(post, 'ups', 0),
                            'downs': getattr(post, 'downs', 0),
                            'score': getattr(post, 'score', 0),
                            'comments': top_comments  # Store list of comments
                        })

            except Exception as e:
                print(f"Error searching subreddit for keyword '{keyword}': {e}")

        return pd.DataFrame(search_results) if search_results else pd.DataFrame(columns=[
            'id', 'title', 'selftext', 'created', 'upvote_ratio', 'ups', 'downs', 'score', 'comments'
        ])