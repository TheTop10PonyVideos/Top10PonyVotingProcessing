import tkinter as tk
from tkinter import ttk, filedialog
from modules import (# Import all the neccesary modules lol
    duplicate,
    duration_check,
    fuzzy_check,
    blacklist,
    upload_date,
    uploader_occurence,
    data_pulling,
    init
)
import os
import shutil
# Main program to be run
debugging = True

def browse_file():  # Function that asks for a CSV file
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    entry_var.set(file_path)


def run_checks():  # Function that runs selected rules
    start_csv_file = entry_var.get()
    csv_file = "outputs/temp_outputs/shifted_cells.csv"
    data_pulling.set_count(start_csv_file)
    init.add_empty_cells(start_csv_file)  # Add the empty cells
    fuzzy_check.links_to_titles(csv_file)
    if duplicate_var.get() == False:
        shutil.copyfile("outputs/temp_outputs/titles_output.csv", "outputs/temp_outputs/processed.csv")
    # Check which checkboxes are selected and run the corresponding checks
    #duplicate.check_duplicates(csv_file)
    if duplicate_var.get():
        duplicate.check_duplicates(csv_file)
    if blacklist_var.get():
        blacklist.check_blacklist(csv_file)
    if upload_date_var.get():
        upload_date.check_dates(csv_file)
    if duration_var.get():
        duration_check.check_duration(csv_file)
    if fuzzy_var.get():
        fuzzy_check.fuzzy_match()
    if uploader_occurrence_var.get():
        uploader_occurence.check_uploader_occurrence()
    fuzzy_check.delete_first_cell()
    if not debugging:
        # Delete outputs if present
        delete_if_present("outputs/temp_outputs/processed_blacklist.csv")
        delete_if_present("outputs/temp_outputs/processed_duplicates.csv")
        delete_if_present("outputs/temp_outputs/processed_fuzzlist.csv")
        delete_if_present("outputs/temp_outputs/processed_dates.csv")
        delete_if_present("outputs/temp_outputs/durations_output.csv")
        delete_if_present("outputs/temp_outputs/titles_output.csv")
        delete_if_present("outputs/temp_outputs/uploaders_output.csv")
        delete_if_present("outputs/temp_outputs/shifted_cells.csv")
        delete_if_present("outputs/temp_outputs/processed.csv")


def delete_if_present(filepath):  # Deletes file if present
    if os.path.exists(filepath):
        os.remove(filepath)


# Creating the GUI
root = tk.Tk()
root.title("Top 10 Pony Video Squeezer 3000")

entry_var = tk.StringVar()
entry = ttk.Entry(root, textvariable=entry_var)
entry.pack(padx=10, pady=10)

browse_button = ttk.Button(root, text="Browse", command=browse_file)
browse_button.pack(pady=10)

# Checkboxes for various checks
duplicate_var = tk.BooleanVar()
duplicate_checkbox = ttk.Checkbutton(root, text="Duplicate Check", variable=duplicate_var)
duplicate_checkbox.pack()

blacklist_var = tk.BooleanVar()
blacklist_checkbox = ttk.Checkbutton(root, text="Blacklist Check", variable=blacklist_var)
blacklist_checkbox.pack()

upload_date_var = tk.BooleanVar()
upload_date_checkbox = ttk.Checkbutton(root, text="Upload Date Check", variable=upload_date_var)
upload_date_checkbox.pack()

duration_var = tk.BooleanVar()
duration_checkbox = ttk.Checkbutton(root, text="Duration Check", variable=duration_var)
duration_checkbox.pack()

fuzzy_var = tk.BooleanVar()
fuzzy_checkbox = ttk.Checkbutton(root, text="Fuzzy Check", variable=fuzzy_var)
fuzzy_checkbox.pack()

uploader_occurrence_var = tk.BooleanVar()
uploader_occurrence_checkbox = ttk.Checkbutton(root, text="Uploader Occurrence Check", variable=uploader_occurrence_var)
uploader_occurrence_checkbox.pack()

run_button = ttk.Button(root, text="Run Checks", command=run_checks)
run_button.pack()

root.mainloop()
