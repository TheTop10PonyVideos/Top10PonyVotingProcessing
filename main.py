import tkinter as tk
from tkinter import ttk, filedialog
from modules import duplicate
from modules import blacklist
from modules import durationcheck
from modules import fuzzycheck
from modules import upload_date
from modules import data_pulling
from modules import init
import os


def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    entry_var.set(file_path)


def run_checks():
    start_csv_file = entry_var.get()
    csv_file = "outputs/shifted_cells.csv"
    data_pulling.set_count(start_csv_file)
    init.add_empty_cells(start_csv_file)
    fuzzycheck.links_to_titles(csv_file)
    duplicate.check_duplicates(csv_file)
    blacklist.check_blacklist(csv_file)
    upload_date.check_dates(csv_file)
    durationcheck.check_duration(csv_file)
    fuzzycheck.fuzzy_match()
    fuzzycheck.delete_first_cell()
    fuzzycheck.delete_first_cell()

    delete_if_present("outputs/processed_blacklist.csv")
    delete_if_present("outputs/processed_duplicates.csv")
    delete_if_present("outputs/processed_fuzzlist.csv")
    delete_if_present("outputs/processed_dates.csv")
    delete_if_present("outputs/durations_output.csv")
    delete_if_present("outputs/titles_output.csv")
    delete_if_present("outputs/uploaders_output.csv")
    delete_if_present("outputs/shifted_cells.csv")


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
