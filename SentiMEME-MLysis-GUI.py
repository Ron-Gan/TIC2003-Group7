import tkinter as tk
from tkinter import *
from tkcalendar import Calendar as cal, DateEntry
from scripts.coin_list_generator import CoinListGenerator
from scripts.export_csv import ExportCSV
from scripts.Numeric_Analysis_Subsystem import NumericSubsystem
from scripts.reddit_api_fetch import RedditAPI
from scripts.topic_model import RedditTopicModel
from scripts.sentiment_analysis import RedditSentimentAnalysis

from datetime import time
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

def init_start_time(start_date,end_date,end_time):
    if start_date == end_date: # Set start_time to midnight
        start_time = time(0,0,0,0)
    else:
        start_time = end_time  # Set start_time to the same as end_time
    return start_time

def process_ticker(ticker):
    ticker = ticker.split(' ')
    ticker[1]=ticker[1][1:-1]
    return ticker

def analyse():
    ticker = process_ticker(ticker_entry.get())
    ticker_id = ticker[0]
    start_date = start_date_label.get()  # Get user-selected start date
    end_date = datetime.now().date()  # Static end date as today
    end_time = datetime.now().time()#.strftime("%H:%M:%S")  # Static end time as current time (formatted)
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    start_time = init_start_time(start_date,end_date,end_time)
    subreddit = subreddit_entry.get()
    subreddit = subreddit[2:]  # Remove 'r/' from the output

    start_datetime = datetime.combine(start_date,start_time)
    end_datetime = datetime.combine(end_date,end_time)

    """
    Numeric Analysis Portion
    """
    number_analysis = NumericSubsystem(start_datetime,end_datetime,ticker_id, "market data")
    number_analysis.extract_data()
    ExportCSV(number_analysis)

    """
    Text Analysis Portion
    """
    print("Fetching Reddit posts...")
    reddit_api = RedditAPI(subreddit, [ticker[1]], start_datetime, end_datetime)
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
    ExportCSV(sentiment_analysis)
    print("Analysis Completed.")

    print(ticker, start_date, start_time, end_date, end_time, subreddit)

# Create a frame for layout
frame = tk.Frame(bg='blue')

# Title label
title_label = tk.Label(frame, text="SentiMEME-MLysis", font=("Arial Bold", 30), bg='blue', fg='white')
title_label.grid(row=0, column=0, columnspan=2, pady=20)

# Ticker label and entry
ticker_label = tk.Label(frame, text="Select Ticker:", font=("Arial Bold", 18), bg='blue', fg='white')
ticker_label.grid(row=1, column=0)

ticker_var = tk.StringVar()  # Default value

#Generates coin list for dropdown
coinlist = CoinListGenerator().get_list()
print("Coin List generated successfully!")

# Create a Toplevel window for the dropdown list
dropdown_window = tk.Toplevel(window)
dropdown_window.withdraw()  # Hide the window initially
dropdown_window.overrideredirect(True)  # Remove window decorations

# Create a Listbox with a Scrollbar
dropdown_listbox = tk.Listbox(dropdown_window, height=5, width=20)  # Set a fixed width
scrollbar = tk.Scrollbar(dropdown_window, orient=tk.VERTICAL, command=dropdown_listbox.yview)
dropdown_listbox.configure(yscrollcommand=scrollbar.set)

# Pack the Listbox and Scrollbar
dropdown_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

def update_dropdown(event=None):
    """Filters the dropdown list options as the user types."""
    prefix = ticker_var.get()
    dropdown_listbox.delete(0, tk.END)  # Clear the current list

    if prefix == "":
        for coin in coinlist:
            dropdown_listbox.insert(tk.END, coin)  # Show all options if empty
    else:
        filtered_tickers = [coin for coin in coinlist if prefix in coin]
        for coin in filtered_tickers:
            dropdown_listbox.insert(tk.END, coin)  # Update dropdown list

    # Adjust the width of the Listbox to fit the longest item
    max_width = max(len(coin) for coin in dropdown_listbox.get(0, tk.END))
    dropdown_listbox.configure(width=max_width + 2)  # Add some padding

    # Position the dropdown window below the entry widget
    if ticker_entry.winfo_ismapped():  # Check if the entry widget is visible
        x = ticker_entry.winfo_rootx()
        y = ticker_entry.winfo_rooty() + ticker_entry.winfo_height()
        dropdown_window.geometry(f"+{x}+{y}")
        dropdown_window.deiconify()  # Show the dropdown window

def hide_dropdown(event=None):
    """Hide the dropdown list when focus is lost."""
    # Check if the mouse is over the dropdown window or its children
    if not dropdown_window.winfo_containing(dropdown_window.winfo_pointerx(), dropdown_window.winfo_pointery()):
        dropdown_window.withdraw()

def select_ticker(event=None):
    """Set the selected ticker in the entry field."""
    selected = dropdown_listbox.get(tk.ACTIVE)
    if selected:
        ticker_var.set(selected)
    hide_dropdown()

# Create an Entry widget for typing
ticker_entry = tk.Entry(frame, textvariable=ticker_var)
ticker_entry.grid(row=1, column=1, columnspan=3, pady=10)
ticker_entry.insert(0, "Search for a ticker")  # Default value

# Bind the update_dropdown function to the search input
ticker_entry.bind("<KeyRelease>", update_dropdown)
ticker_entry.bind("<FocusOut>", hide_dropdown)  # Hide dropdown when focus is lost

# Bind the dropdown listbox to select a ticker
dropdown_listbox.bind("<ButtonRelease-1>", select_ticker)
dropdown_listbox.bind("<Return>", select_ticker)  # Allow selection with Enter key

# Prevent the dropdown from closing when interacting with the scrollbar
scrollbar.bind("<ButtonPress-1>", lambda event: "break")
scrollbar.bind("<ButtonRelease-1>", lambda event: "break")

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
subreddit_entry = tk.Entry(frame,textvariable=subreddit_var)
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
