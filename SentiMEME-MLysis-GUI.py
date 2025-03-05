import tkinter as tk
from tkinter import *
from tkcalendar import Calendar as cal, DateEntry
from scripts.Numeric_Analysis_Subsystem import NumericAnalysis
from scripts.reddit_api_fetch import RedditAPI
from scripts.topic_model import RedditTopicModel
from scripts.sentiment_analysis import RedditSentimentAnalysis


from datetime import datetime

window=tk.Tk()
window.title("SentiMEME-MLysis")
window.geometry('500x300')
window.configure(background='blue')

# Define end date and end time globally
end_date = datetime.now().date()  # Static end date as today
end_time = datetime.now().time().strftime("%H:%M:%S")  # Static end time as current time (formatted)

def get_date():
    selected_date = cal.get_date()
    print(f"Selected date: {selected_date}")

def analyse():
    ticker = ticker_entry.get()
    start_date = start_date_label.get()  # Get user-selected start date
    end_date = datetime.now().date()  # Static end date as today
    end_time = datetime.now().time()#.strftime("%H:%M:%S")  # Static end time as current time (formatted)
    start_time = end_time  # Set start_time to the same as end_time
    subreddit = subreddit_entry.get()

    start_date = datetime.strptime(start_date,"%Y-%m-%d").date()
    start_datetime = datetime.combine(start_date,start_time)
    end_datetime = datetime.combine(end_date,end_time)

    NumericAnalysis(start_datetime,end_datetime,ticker)

    print("Fetching Reddit posts...")
    reddit_api = RedditAPI(subreddit, [ticker], start_datetime, end_datetime)
    reddit_df = reddit_api.search_subreddit()

    if reddit_df.empty:
        print("No posts found for the selected criteria.")
        return

    # Perform topic modeling
    print("Performing topic modeling...")
    topic_model = RedditTopicModel(reddit_df)
    topic_model.initialize_model()
    topic_model.fit_transform()
    topic_model.create_topic_dataframe()
    topic_df = topic_model.get_topic_dataframe()

    # Perform sentiment analysis
    print("Performing sentiment analysis...")
    sentiment_analysis = RedditSentimentAnalysis(topic_df)
    sentiment_analysis.initialize_model()
    sentiment_analysis.analyze_sentiment(batch_size=16)
    sentiment_df = sentiment_analysis.get_sentiment_dataframe()

    # Show results
    print("\nAnalysis Completed! Here are the results:")
    print(sentiment_df.head())

    print(ticker, start_date, start_time, end_date, end_time, subreddit)

# Create a frame for layout
frame = tk.Frame(bg='blue')

# Title label
title_label = tk.Label(frame, text="SentiMEME-MLysis", font=("Arial Bold", 30), bg='blue', fg='white')
title_label.grid(row=0, column=0, columnspan=2, pady=20)

# Ticker label and entry
ticker_label = tk.Label(frame, text= "Enter desired ticker:", font=("Arial Bold", 18), bg='blue', fg='white')
ticker_label.grid(row=1, column=0)
ticker_entry = tk.Entry(frame)
ticker_entry.grid(row=1, column=1, columnspan=3, pady=10)

# Date range label
range_label = tk.Label(frame, text= "Enter analysis start date:", font=("Arial Bold", 18), bg='blue', fg='white')
range_label.grid(row=2, column=0)

# Date for end of range
end_label = tk.Label(frame, text=f"End Date: {datetime.now().date()}", bg='blue', fg='white')

# Date picker for start of range
start_date_label = DateEntry(frame, date_pattern='yyyy-mm-dd', maxdate=datetime.now().date())
start_date_label.grid(row=2, column=1, padx=5, pady=5)

# Time for start and end of range
start_time_label = tk.Label(frame, text=f"Start Time: {end_time}", bg='blue', fg='white')

# Subreddit label and entry
subreddit_label = tk.Label(frame, text= "Enter desired subreddit:", font=("Arial Bold", 18), bg='blue', fg='white')
subreddit_label.grid(row=3, column=0)

# Subreddit input with default 'r/' prefix
subreddit_var = tk.StringVar(value='r/')  # Default value
subreddit_entry = tk.Entry(frame, textvariable=subreddit_var)
subreddit_entry.grid(row=3, column=1, columnspan=3, pady=10)


# Prevent editing or typing before 'r/'
def enforce_r_prefix(*args):
    if not subreddit_var.get().startswith('r/'):
        subreddit_var.set('r/' + subreddit_var.get().lstrip('r/'))

subreddit_var.trace_add('write', enforce_r_prefix)

# Prevent cursor from moving left of 'r/'
def restrict_cursor(event):
    # Get the current cursor position
    cursor_index = subreddit_entry.index(tk.INSERT)
    # Prevent cursor from moving before the 3rd character (after 'r/')
    if cursor_index < 2:
        subreddit_entry.icursor(2)

# Prevent typing before 'r/'
def prevent_insertion(event):
    # Prevent text insertion before 'r/'
    cursor_index = subreddit_entry.index(tk.INSERT)
    if cursor_index < 2:
        return "break"

# Prevent backspace from deleting 'r/'
def prevent_backspace(event):
    # Prevent backspace if cursor is at or before 'r/'
    cursor_index = subreddit_entry.index(tk.INSERT)
    if cursor_index <= 2:
        return "break"

# Bind events to the subreddit entry
subreddit_entry.bind("<KeyRelease>", restrict_cursor)     # Prevent cursor movement left of 'r/'
subreddit_entry.bind("<Key>", prevent_insertion)          # Prevent insertion before 'r/'
subreddit_entry.bind("<BackSpace>", prevent_backspace)    # Prevent backspace from deleting 'r/'

# Button to run analysis
analyse_button = tk.Button(frame, text="Analyse", font=("Arial Bold", 18), bg='white', fg='grey', command=analyse)
analyse_button.grid(row=4, column=0, columnspan=2, pady=20)

# Pack the frame
frame.pack()

# Run the application
window.mainloop()
