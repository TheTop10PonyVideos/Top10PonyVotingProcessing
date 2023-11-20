import tkinter as tk
from tkinter import ttk, filedialog
from modules import duplicate
from modules import blacklist
from modules import durationcheck
from modules import fuzzycheck
from modules import upload_date
from modules import data_pulling
import os


def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    entry_var.set(file_path)


def run_checks():
    csv_file = entry_var.get()
    data_pulling.setCount(csv_file)
    fuzzycheck.linksToTitles(csv_file)
    duplicate.checkDuplicates(csv_file)
    blacklist.checkBlacklist(csv_file)
    upload_date.checkDates(csv_file)
    durationcheck.checkDuration(csv_file)
    fuzzycheck.adapt_output_csv()

    if os.path.exists("outputs/processedblacklist.csv"):
        os.remove("outputs/processedblacklist.csv")
    if os.path.exists("outputs/processedduplicates.csv"):
        os.remove("outputs/processedduplicates.csv")
    if os.path.exists("outputs/processedfuzzlist.csv"):
        os.remove("outputs/processedfuzzlist.csv")
    if os.path.exists("outputs/processedDates.csv"):
        os.remove("outputs/processedDates.csv")
    if os.path.exists("outputs/durations_output.csv"):
        os.remove("outputs/durations_output.csv")
    if os.path.exists("outputs/titles_output.csv"):
        os.remove("outputs/titles_output.csv")
    if os.path.exists("outputs/uploaders_output.csv"):
        os.remove("outputs/uploaders_output.csv")


root = tk.Tk()
root.title("Check Script")

entry_var = tk.StringVar()
entry = ttk.Entry(root, textvariable=entry_var)
entry.pack(padx=10, pady=10)


browse_button = ttk.Button(root, text="Browse", command=browse_file)
browse_button.pack(pady=10)

run_button = ttk.Button(root, text="Run Checks", command=run_checks)
run_button.pack()

root.mainloop()
