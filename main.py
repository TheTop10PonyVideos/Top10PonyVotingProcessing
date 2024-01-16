import tkinter as tk
from tkinter import ttk, filedialog
from modules import duplicate
from modules import blacklist
from modules import duration_check
from modules import fuzzy_check
from modules import upload_date
from modules import uploader_occurence
from modules import (
    data_pulling,
    init,
    duplicate,
    blacklist,
    duration_check,
    fuzzy_check,
    upload_date,
)  # Import of all the necesary functions from the modules folder
import os


# Mane program to be run

debugging = True  # Change to False for only final output


def browse_file():  # Function that asks for a CSV file
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    entry_var.set(file_path)


def run_checks():  # Function that runs all the rules
    start_csv_file = entry_var.get()
    csv_file = "outputs/temp_outputs/shifted_cells.csv"
    data_pulling.set_count(start_csv_file)
    init.add_empty_cells(start_csv_file)

    fuzzy_check.links_to_titles(csv_file)
    duplicate.check_duplicates(csv_file)
    blacklist.check_blacklist(csv_file)
    upload_date.check_dates(csv_file)
    duration_check.check_duration(csv_file)
    fuzzy_check.fuzzy_match()
    fuzzy_check.delete_first_cell()
    uploader_occurence.check_uploader_occurence()

    if not debugging:   # Calls deleting outputs if present
        delete_if_present("outputs/temp_outputs/processed_blacklist.csv")
        delete_if_present("outputs/temp_outputs/processed_duplicates.csv")
        delete_if_present("outputs/temp_outputs/processed_fuzzlist.csv")
        delete_if_present("outputs/temp_outputs/processed_dates.csv")
        delete_if_present("outputs/temp_outputs/durations_output.csv")
        delete_if_present("outputs/temp_outputs/titles_output.csv")
        delete_if_present("outputs/temp_outputs/uploaders_output.csv")
        delete_if_present("outputs/temp_outputs/shifted_cells.csv")
        delete_if_present("outputs/temp_outputs/processed.csv")


def delete_if_present(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)


root = tk.Tk()  # Creating the GUI
root.title("Check Script")

entry_var = tk.StringVar()
entry = ttk.Entry(root, textvariable=entry_var)
entry.pack(padx=10, pady=10)


browse_button = ttk.Button(root, text="Browse", command=browse_file)
browse_button.pack(pady=10)

run_button = ttk.Button(root, text="Run Checks", command=run_checks)
run_button.pack()

root.mainloop()
