import tkinter as tk
from tkinter import *
from tkcalendar import Calendar as cal, DateEntry

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
    end_time = datetime.now().time().strftime("%H:%M:%S")  # Static end time as current time (formatted)
    start_time = end_time  # Set start_time to the same as end_time
    subreddit = subreddit_entry.get()

    print(ticker, start_date, start_time, end_date, end_time, subreddit)

frame = tk.Frame(bg='blue')

title_label = tk.Label(frame, text="SentiMEME-MLysis", font=("Arial Bold", 30), bg='blue', fg='white')

title_label.grid(row=0, column=0, columnspan=2, pady=20)

ticker_label = tk.Label(frame, text= "Enter desired ticker:", font=("Arial Bold", 18), bg='blue', fg='white')
ticker_entry = tk.Entry(frame)

ticker_label.grid(row=1, column=0)
ticker_entry.grid(row=1, column=1, columnspan=3, pady=10)

range_label = tk.Label(frame, text= "Enter analysis start date:", font=("Arial Bold", 18), bg='blue', fg='white')
range_label.grid(row=2, column=0)

# Date for end of range
end_label = tk.Label(frame, text=f"End Date: {datetime.now().date()}", bg='blue', fg='white')

# Date picker for start of range
start_date_label = DateEntry(frame, date_pattern='yyyy-mm-dd')
start_date_label.grid(row=2, column=1, padx=5, pady=5)

# Time for start and end of range
start_time_label = tk.Label(frame, text=f"Start Time: {end_time}", bg='blue', fg='white')

subreddit_label = tk.Label(frame, text= "Enter desired subreddit:", font=("Arial Bold", 18), bg='blue', fg='white')
subreddit_label.grid(row=3, column=0)

subreddit_entry = tk.Entry(frame)
subreddit_entry.grid(row=3, column=1, columnspan=3, pady=10)

analyse_button = tk.Button(frame, text="Analyse", font=("Arial Bold", 18), bg='white', fg='grey', command=analyse)
analyse_button.grid(row=4, column=0, columnspan=2, pady=20)

frame.pack()

window.mainloop()