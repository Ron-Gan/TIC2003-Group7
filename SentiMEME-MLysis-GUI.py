import tkinter as tk
import logging
import sys
from tkinter import Toplevel, StringVar, Listbox, Scrollbar, Entry, Label, Button, messagebox
from tkcalendar import Calendar
from datetime import datetime, time, timedelta
from scripts.coin_list_generator import CoinListGenerator
from scripts.export_csv import ExportCSV
from scripts.Numeric_Analysis_Subsystem import NumericSubsystem
from scripts.reddit_api_fetch import RedditAPI
from scripts.topic_model import RedditTopicModel
from scripts.sentiment_analysis import RedditSentimentAnalysis
from pathlib import Path
import os
import subprocess

with open("app.log", "w") as log_file:
    log_file.write("")  # Clears the log file

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class SentiMemeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SentiMEME-MLysis")
        self.root.geometry('800x500')
        self.root.configure(background='blue')

        self.end_date = datetime.now().date()
        self.end_time = datetime.now().time().strftime("%H:%M:%S")

        self.calendar_window = None
        self.status_label = None

        self.setup_ui()

    def setup_ui(self):
        self.frame = tk.Frame(self.root, bg='blue')
        self.frame.pack(padx=20, pady=20)

        # Configure grid columns for consistent alignment
        self.frame.columnconfigure(0, weight=1, minsize=250)  # Label column
        self.frame.columnconfigure(1, weight=3)  # Entry column
        self.frame.columnconfigure(2, weight=1)  # Button column (for calendar)

        # Title
        Label(self.frame, text="SentiMEME-MLysis", font=("Arial Bold", 30),
              bg='blue', fg='white').grid(row=0, column=0, columnspan=3, pady=20)

        # Ticker Selection
        Label(self.frame, text="Select Ticker:", font=("Arial Bold", 18),
              bg='blue', fg='white').grid(row=1, column=0, sticky='w', pady=5)

        self.ticker_var = StringVar(value="Search for a ticker")
        try:
            self.coinlist = CoinListGenerator().get_list()
        except RuntimeError as e:
            messagebox.showerror("Unexpected Error", str(e))
            self.root.destroy()

        self.ticker_entry = Entry(self.frame, textvariable=self.ticker_var, font=("Arial", 12))
        self.ticker_entry.grid(row=1, column=1, columnspan=2, sticky='ew', pady=5, padx=5)
        self.ticker_entry.bind("<FocusIn>", self.on_click)
        self.ticker_entry.bind("<KeyRelease>", self.update_dropdown)
        self.ticker_entry.bind("<FocusOut>", self.hide_dropdown)

        # Date Selection
        Label(self.frame, text="Analysis start date:", font=("Arial Bold", 18),
              bg='blue', fg='white').grid(row=2, column=0, sticky='w', pady=5)

        self.date_frame = tk.Frame(self.frame, bg='blue')
        self.date_frame.grid(row=2, column=1, sticky='ew')

        self.start_date_var = StringVar(value=(self.end_date - timedelta(days=15)).strftime('%d/%m/%Y'))
        self.start_date_entry = Entry(self.date_frame, textvariable=self.start_date_var,
                                      font=("Arial", 12), width=20)
        self.start_date_entry.grid(row=0, column=0, sticky='ew')

        Button(self.date_frame, text="📅", command=self.show_calendar,
               font=("Arial", 12), width=3).grid(row=0, column=1, padx=(5, 0))

        # Subreddit Entry
        Label(self.frame, text="Subreddit to analyze:", font=("Arial Bold", 18),
              bg='blue', fg='white').grid(row=3, column=0, sticky='w', pady=5)

        self.subreddit_var = StringVar(value='r/')
        self.subreddit_entry = Entry(self.frame, textvariable=self.subreddit_var,
                                     font=("Arial", 12))
        self.subreddit_entry.grid(row=3, column=1, columnspan=2, sticky='ew', pady=5, padx=5)
        self.subreddit_var.trace_add('write', self.enforce_r_prefix)

        self.subreddit_entry.bind("<KeyRelease>", self.restrict_cursor)
        self.subreddit_entry.bind("<Key>", self.prevent_insertion)
        self.subreddit_entry.bind("<BackSpace>", self.prevent_backspace)
        self.subreddit_entry.bind("<ButtonRelease-1>", self.restrict_cursor)

        # Analyze Button
        self.analyse_button = Button(self.frame, text="Analyse", font=("Arial Bold", 18),
                                     state="disabled", bg='light grey', fg='dark grey',
                                     command=self.analyse)
        self.analyse_button.grid(row=4, column=0, columnspan=3, pady=20)

        # Status label
        self.status_label = Label(self.frame, text="", bg='blue', fg='white', font=("Arial", 12))
        self.status_label.grid(row=5, column=0, columnspan=3, pady=(0, 10))

        # Dropdown setup
        self.setup_dropdown()
        self.check_fields()

    def setup_dropdown(self):
        self.dropdown_window = Toplevel(self.root)
        self.dropdown_window.withdraw()
        self.dropdown_window.overrideredirect(True)

        self.dropdown_listbox = Listbox(self.dropdown_window, height=5, width=20, font=("Arial", 12))
        self.scrollbar = Scrollbar(self.dropdown_window, orient=tk.VERTICAL, command=self.dropdown_listbox.yview)
        self.dropdown_listbox.configure(yscrollcommand=self.scrollbar.set)

        self.dropdown_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.dropdown_listbox.bind("<ButtonRelease-1>", self.select_ticker)
        self.dropdown_listbox.bind("<Return>", self.select_ticker)

    def show_calendar(self):
        if self.calendar_window and self.calendar_window.winfo_exists():
            self.calendar_window.lift()  # Bring it to front if it's already open
            return

        self.calendar_window = Toplevel(self.root)  # assign to self.calendar_window
        self.calendar_window.title("Select Date")

        cal = Calendar(self.calendar_window,
                       selectmode='day',
                       mindate=self.end_date - timedelta(days=15),
                       maxdate=self.end_date,
                       font=("Arial", 12),
                       date_pattern='dd/mm/yyyy')  # Set date format here
        cal.pack(padx=10, pady=10)
        
        Button(self.calendar_window, 
               text="OK", 
               command=lambda: self.set_date(cal, self.calendar_window),
               font=("Arial", 12)).pack(pady=5)

    def set_date(self, cal, top):
        selected_date = cal.get_date()
        self.start_date_var.set(selected_date)
        top.destroy()
        self.check_fields()

    def check_fields(self):
        ticker = self.ticker_var.get().strip()
        subreddit = self.subreddit_var.get().strip()
        start_date = self.start_date_var.get()

        if (ticker and ticker != "Search for a ticker" and
                subreddit.startswith("r/") and len(subreddit) > 2 and
                start_date):
            self.analyse_button.config(state="normal", bg='white', fg='green')
        else:
            self.analyse_button.config(state="disabled", bg='light grey', fg='dark grey')

        self.root.after(300, self.check_fields)

    def analyse(self):
        # Disable button during processing
        self.analyse_button.config(state="disabled", bg='light grey', fg='dark grey')
        self.status_label.config(text="Running analysis...")
        self.root.update_idletasks()

        try:
            ticker = self.ticker_var.get().split(' ')[0]
            start_date = datetime.strptime(self.start_date_var.get(), "%d/%m/%Y").date()
            subreddit = self.subreddit_var.get()[2:]

            start_datetime = datetime.combine(
                start_date,
                time(0, 0, 0) if (start_date == self.end_date or start_date - self.end_date > timedelta(days=90)) else datetime.now().time()
            )

            end_datetime = datetime.combine(self.end_date, datetime.now().time())

            # Numeric Analysis
            number_analysis = NumericSubsystem(start_datetime, end_datetime, ticker, "market data")
            number_analysis.extract_data()
            number_analysis.convert_df()
            numeric_df = number_analysis.get_numeric_data_df()
            logging.info("Numeric Analysis Completed!")

            # Reddit Extraction
            reddit_api = RedditAPI(subreddit, [ticker], start_datetime, end_datetime)
            reddit_df = reddit_api.search_subreddit()
            if reddit_df.empty:
                self.status_label.config(text="No Reddit posts found.")
                return

            # Topic Modelling
            try:
                topic_model = RedditTopicModel(reddit_df)
                topic_model.initialize_model()
                topic_model.fit_transform()
                topic_model.process_topics()
                topic_df = topic_model.get_topic_dataframe()
                logging.info("Topic Modelling Completed!")
            except Exception as topic_error:
                logging.error(f"Topic modelling failed: {topic_error}")
                messagebox.showwarning("Topic Modelling Failed due to insufficient post", "Proceeding with sentiment analysis only.")
                topic_df = reddit_df.copy()
                topic_df["topic"] = -1

            # Sentiment Analysis
            sentiment_analysis = RedditSentimentAnalysis(topic_df)
            sentiment_analysis.initialize_model()
            sentiment_analysis.analyze_sentiment(batch_size=16)
            sentiment_analysis.finalize_sentiment_dataframe()
            sentiment_df = sentiment_analysis.get_sentiment_dataframe()
            logging.info("Text Analysis Completed!")

            # Merged Export
            ExportCSV(df_text=sentiment_df, df_num=numeric_df)
            messagebox.showinfo("Analysis Completed","Analysis Completed Successfully!")

            self.find_and_open_twbx()

        except ValueError as e:
            error_msg = f"Error parsing date: {e}"
            logging.error(error_msg)
            messagebox.showerror("Date Error", error_msg)
            self.analyse_button.config(state="normal", bg='white', fg='green')
            self.status_label.config(text="")

        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logging.error(error_msg)
            messagebox.showerror("Unexpected Error", error_msg)
            self.analyse_button.config(state="normal", bg='white', fg='green')
            self.status_label.config(text="")

    def find_and_open_twbx(self):
        # Define the target file name
        filename = "SentiMEME-MLysis-Dashboard_FINAL.twbx"

        # Go one level up from the current script's directory
        parent_dir = Path(__file__).resolve().parent.parent
        twbx_file = parent_dir / filename

        # Check if file exists
        if not twbx_file.exists():
            messagebox.showwarning("No File Found", f"'{filename}' not found one level up.")
            self.analyse_button.config(state="normal", bg='white', fg='green')
            self.status_label.config(text="")
            return

        try:
            self.status_label.config(text="Opening SentiMEME-MLysis-Dashboard_FINAL.twbx")
            
            # Open with default application            
            if os.name == 'nt':  # Windows
                os.startfile(twbx_file)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(["open", str(twbx_file)])
            else:  # Linux/Unix
                subprocess.run(["xdg-open", str(twbx_file)])

            self.status_label.config(text="Done!")

            logging.info(f"Opened .twbx file: {twbx_file}")

        except Exception as e:
            logging.error(f"Failed to open .twbx: {e}")
            messagebox.showerror("Error", f"Failed to open the .twbx file:\n{e}")
            self.analyse_button.config(state="normal", bg='white', fg='green')
            self.status_label.config(text="")

    def update_dropdown(self, event=None):
        self.dropdown_listbox.delete(0, tk.END)
        prefix = self.ticker_var.get().lower()
        filtered_tickers = [coin for coin in self.coinlist if prefix in coin.lower()]
        for coin in filtered_tickers:
            self.dropdown_listbox.insert(tk.END, coin)
        if self.dropdown_listbox.size() > 0:
            x = self.ticker_entry.winfo_rootx()
            y = self.ticker_entry.winfo_rooty() + self.ticker_entry.winfo_height()
            self.dropdown_window.geometry(f"+{x}+{y}")
            self.dropdown_window.deiconify()

    def hide_dropdown(self, event=None):
        if event and hasattr(event, 'widget'):
            if event.widget == self.ticker_entry:
                self.root.after(100, lambda: self.dropdown_window.withdraw())
        else:
            self.root.after(100, lambda: self.dropdown_window.withdraw())

    def select_ticker(self, event=None):
        """Set the selected ticker in the entry field."""
        selected_index = self.dropdown_listbox.curselection()
        if selected_index:
            selected_ticker = self.dropdown_listbox.get(selected_index[0])
            self.ticker_var.set(selected_ticker)
        self.hide_dropdown()

    def on_click(self, event):
        if self.ticker_var.get() == "Search for a ticker":
            self.ticker_var.set("")

    def enforce_r_prefix(self, *args):
        current = self.subreddit_var.get()
        if not current.startswith('r/'):
            self.subreddit_var.set('r/' + current.lstrip('r/'))

    def restrict_cursor(self, event):
        if self.subreddit_entry.index(tk.INSERT) < 2:
            self.subreddit_entry.icursor(2)  # Force cursor after "r/"
        
    def prevent_backspace(self, event):
        if self.subreddit_entry.index(tk.INSERT) <= 2:
            return "break"
    
    def prevent_insertion(self, event):
        if self.subreddit_entry.index(tk.INSERT) < 2:
            return "break"

if __name__ == "__main__":
    root = tk.Tk()
    app = SentiMemeApp(root)
    root.mainloop()