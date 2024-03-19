"""Top 10 Pony Video Squeezer 3000 application."""
import os, shutil, sys
import tkinter as tk
from tkinter import ttk, filedialog
from modules import (  # Import all the neccesary modules lol
    duplicate,
    duration_check,
    fuzzy_check,
    blacklist,
    upload_date,
    uploader_occurence,
    data_pulling,
    init,
    uploader_diversity,
)
from classes.ui import CSVEditor

def browse_file_csv():
    """Handler for the "Browse" button. Opens a file dialog and sets the global
    variable `entry_var` to the selected file.
    """
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    entry_var.set(file_path)


def run_checks():
    """Handler for the "Run Checks" button."""

    selected_csv_file = entry_var.get()
    if selected_csv_file.strip() == "":
        tk.messagebox.showinfo("Error", "Please select a CSV file first.")
        return

    init.add_empty_cells(
        selected_csv_file, "outputs/shifted_cells.csv"  # input  # output
    )

    fuzzy_check.links_to_titles(
        "outputs/shifted_cells.csv",  # input
        "outputs/temp_outputs/titles_output.csv",  # output 1
        "outputs/temp_outputs/uploaders_output.csv",  # output 2
        "outputs/temp_outputs/durations_output.csv",  # output 3
    )

    if check_vars["duplicate"].get() == False:
        shutil.copyfile(
            "outputs/temp_outputs/titles_output.csv",
            "outputs/temp_outputs/processed.csv",
        )
    if check_vars["duplicate"].get():
        duplicate.check_duplicates(
            "outputs/shifted_cells.csv",  # input 1
            "outputs/temp_outputs/titles_output.csv",  # input 2
            "outputs/temp_outputs/processed.csv",  # output
        )

    if check_vars["blacklist"].get():
        blacklist.check_blacklist(
            "outputs/shifted_cells.csv",  # input 1
            "outputs/temp_outputs/processed.csv",  # input 2
            "outputs/temp_outputs/processed.csv",  # output
        )

    if check_vars["upload_date"].get():
        upload_date.check_dates(
            "outputs/shifted_cells.csv",  # input 1
            "outputs/temp_outputs/processed.csv",  # input 2
            "outputs/temp_outputs/processed.csv",  # output
        )

    if check_vars["duration"].get():
        duration_check.check_duration(
            "outputs/shifted_cells.csv",  # input 1
            "outputs/temp_outputs/processed.csv",  # input 2
            "outputs/temp_outputs/processed.csv",  # output
        )

    if check_vars["fuzzy"].get():
        fuzzy_check.fuzzy_match(
            "outputs/temp_outputs/processed.csv",  # input
            "outputs/temp_outputs/titles_output.csv",  # output 1
            "outputs/temp_outputs/uploaders_output.csv",  # output 2
            "outputs/temp_outputs/durations_output.csv",  # output 3
        )

    if check_vars["uploader_occurrence"].get():
        uploader_occurence.check_uploader_occurrence(
            "outputs/temp_outputs/uploaders_output.csv",  # input
            "outputs/processed.csv",  # input 2
            "outputs/processed.csv",  # output
        )

    if check_vars["uploader_diversity"].get():
        uploader_diversity.check_uploader_diversity(
            "outputs/temp_outputs/uploaders_output.csv",  # input
            "outputs/processed.csv",  # input 2
            "outputs/processed.csv",  # output
        )

    # Delete output files if present
    if check_vars["debug"] == False:
        temp_output_file_paths = [
            "outputs/temp_outputs/processed_blacklist.csv",
            "outputs/temp_outputs/processed_duplicates.csv",
            "outputs/temp_outputs/processed_dates.csv",
            "outputs/temp_outputs/durations_output.csv",
            "outputs/temp_outputs/titles_output.csv",
            "outputs/temp_outputs/uploaders_output.csv",
            "outputs/shifted_cells.csv",
            "outputs/temp_outputs/processed.csv",
        ]

        for temp_output_file_path in temp_output_file_paths:
            delete_if_present(temp_output_file_path)

    tk.messagebox.showinfo("Processing Completed", "Processing Completed")


def delete_if_present(filepath):
    """Delete the given file if it exists on the filesystem."""
    if os.path.exists(filepath):
        os.remove(filepath)

# Create GUI
root = tk.Tk()
root.title("Top 10 Pony Video Squeezer 3000")
root.geometry("800x600")

# .ico files unfortunately don't work on Linux due to a known Tkinter issue.
# Current fix is simply to not use the icon on Linux.
if not sys.platform.startswith("linux"):
    root.iconbitmap("images/icon.ico")

# Create Main Object Frame
main_frame = tk.Frame(root)
main_frame.pack(expand=True, fill="both", padx=10, pady=10)

entry_var = tk.StringVar()
entry = ttk.Entry(main_frame, textvariable=entry_var)
entry.pack(padx=10, pady=10)

browse_button = ttk.Button(main_frame, text="Browse", command=browse_file_csv)
browse_button.pack(pady=10)

# Create checkboxes and the variables bound to them.
check_labels = {
    'debug': 'Enable Debug Files (Broken LOL)',
    'duplicate': 'Duplicate Check',
    'blacklist': 'Blacklist Check',
    'upload_date': 'Upload Date Check',
    'duration': 'Duration Check',
    'fuzzy': 'Fuzzy Check',
    'uploader_occurrence': 'Uploader Occurrence Check',
    'uploader_diversity': 'Uploader Diversity Check',
}

check_vars = {key: tk.BooleanVar(value=True) for key in check_labels}

# Disable the debug checkbox by default.
check_vars['debug'] = tk.BooleanVar()

checkboxes = {
    key: ttk.Checkbutton(main_frame, text=check_labels[key], variable=check_vars[key])
    for key in check_labels
}

for key, checkbox in checkboxes.items():
    if key == 'debug':
        checkbox.pack(pady=40)
    else:
        checkbox.pack()

run_button = ttk.Button(main_frame, text="Run Checks", command=run_checks)
run_button.pack()

csv_editor = CSVEditor(main_frame)  # Editor main frame
csv_editor.pack()
root.mainloop()
