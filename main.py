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
    data_pulling.set_count(csv_file)
    fuzzycheck.links_to_titles(csv_file)
    duplicate.check_duplicates(csv_file)
    blacklist.check_blacklist(csv_file)
    upload_date.checkDates(csv_file)
    durationcheck.checkDuration(csv_file)
    fuzzycheck.adapt_output_csv()
    fuzzycheck.deleteFirstCell()

    delete_if_present("outputs/processedblacklist.csv")
    delete_if_present("outputs/processedduplicates.csv")
    delete_if_present("outputs/processedfuzzlist.csv")
    delete_if_present("outputs/processedDates.csv")
    delete_if_present("outputs/durations_output.csv")
    delete_if_present("outputs/titles_output.csv")
    delete_if_present("outputs/uploaders_output.csv")


def delete_if_present(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)


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
