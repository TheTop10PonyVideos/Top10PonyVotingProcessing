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
import os
import shutil
import csv
import sys

# Main program to be run


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

    if duplicate_var.get() == False:
        shutil.copyfile(
            "outputs/temp_outputs/titles_output.csv",
            "outputs/temp_outputs/processed.csv",
        )
    if duplicate_var.get():
        duplicate.check_duplicates(
            "outputs/shifted_cells.csv",  # input 1
            "outputs/temp_outputs/titles_output.csv",  # input 2
            "outputs/temp_outputs/processed.csv",  # output
        )

    if blacklist_var.get():
        blacklist.check_blacklist(
            "outputs/shifted_cells.csv",  # input 1
            "outputs/temp_outputs/processed.csv",  # input 2
            "outputs/temp_outputs/processed.csv",  # output
        )

    if upload_date_var.get():
        upload_date.check_dates(
            "outputs/shifted_cells.csv",  # input 1
            "outputs/temp_outputs/processed.csv",  # input 2
            "outputs/temp_outputs/processed.csv",  # output
        )

    if duration_var.get():
        duration_check.check_duration(
            "outputs/shifted_cells.csv",  # input 1
            "outputs/temp_outputs/processed.csv",  # input 2
            "outputs/temp_outputs/processed.csv",  # output
        )

    if fuzzy_var.get():
        fuzzy_check.fuzzy_match(
            "outputs/temp_outputs/processed.csv",  # input
            "outputs/temp_outputs/titles_output.csv",  # output 1
            "outputs/temp_outputs/uploaders_output.csv",  # output 2
            "outputs/temp_outputs/durations_output.csv",  # output 3
        )

    if uploader_occurrence_var.get():
        uploader_occurence.check_uploader_occurrence(
            "outputs/temp_outputs/uploaders_output.csv",  # input
            "outputs/processed.csv",  # input 2
            "outputs/processed.csv",  # output
        )

    if uploader_diversity_var.get():
        uploader_diversity.check_uploader_diversity(
            "outputs/temp_outputs/uploaders_output.csv",  # input
            "outputs/processed.csv",  # input 2
            "outputs/processed.csv",  # output
        )

    # Delete output files if present
    if debug_var == False:
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
    """Delete the given file, if it exists on the filesystem."""
    if os.path.exists(filepath):
        os.remove(filepath)


class CSVEditor(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.file_path = tk.StringVar()
        self.data = []

        self.create_widgets()

    def create_widgets(self):
        # File select button and save button
        self.browse_button = ttk.Button(self, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=5, padx=5, side="top")
        self.save_button = ttk.Button(
            self, text="Save Changes", command=self.save_changes
        )
        self.save_button.pack(pady=5, padx=5, side="top")

        self.load_button = ttk.Button(
            self, text="Load processed CSV", command=self.load_processed_csv
        )
        self.load_button.pack(pady=5, padx=5, side="top")
        # Frame to hold the CSV data grid
        self.data_frame = tk.Frame(self)
        self.data_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # V-Scrollbar
        self.scrollbar_y = tk.Scrollbar(self.data_frame, orient="vertical")
        self.scrollbar_y.pack(side="right", fill="y")

        # H-Scrollbar
        self.scrollbar_x = tk.Scrollbar(self.data_frame, orient="horizontal")
        self.scrollbar_x.pack(side="bottom", fill="x")

        # Canvas to hold the data
        self.canvas = tk.Canvas(
            self.data_frame,
            bd=0,
            xscrollcommand=self.scrollbar_x.set,
            yscrollcommand=self.scrollbar_y.set,
            width=1200,
            height=700,
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar_x.config(command=self.canvas.xview)
        self.scrollbar_y.config(command=self.canvas.yview)

        self.inner_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", self.on_frame_configure)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.file_path.set(file_path)
            self.load_csv(file_path)

    def load_csv(self, file_path):
        self.data = []
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.data.append(row)

        self.display_csv()

    def load_processed_csv(self):
        processed_csv_file = "outputs/processed.csv"
        self.load_csv(processed_csv_file)

    def display_csv(self):
        # Clear existing widgets
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        # Display CSV data
        for row_idx, row in enumerate(self.data):
            for col_idx, value in enumerate(row):
                entry = tk.Entry(self.inner_frame, width=50)
                entry.grid(row=row_idx, column=col_idx, padx=5, pady=5)
                entry.insert(tk.END, value)
                entry.config(fg="green")
                if (
                    "[SIMILARITY DETECTED" in value
                    or "[DUPLICATE CREATOR]" in value
                    or "[VIDEO TOO OLD]" in value
                ):
                    entry.config(fg="orange")
                if (
                    "[5 CHANNEL RULE]" in value
                    or "[UNSUPPORTED HOST]" in value
                    or "[VIDEO TOO SHORT]" in value
                    or "[BLACKLISTED]" in value
                ):
                    entry.config(fg="red")

    def save_changes(self):
        for row_idx, row in enumerate(self.data):
            for col_idx, _ in enumerate(row):
                entry_widget = self.inner_frame.grid_slaves(
                    row=row_idx, column=col_idx
                )[0]
                self.data[row_idx][col_idx] = entry_widget.get()

        # Save the changes
        with open(self.file_path.get(), "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.data)


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

# Create checkboxes
debug_var = tk.BooleanVar()
debug_checkbox = ttk.Checkbutton(
    main_frame, text="Enable Debug Files (Broken LOL)", variable=debug_var
)
debug_checkbox.pack(pady=40)

duplicate_var = tk.BooleanVar(value=True)
duplicate_checkbox = ttk.Checkbutton(
    main_frame, text="Duplicate Check", variable=duplicate_var
)
duplicate_checkbox.pack()

blacklist_var = tk.BooleanVar(value=True)
blacklist_checkbox = ttk.Checkbutton(
    main_frame, text="Blacklist Check", variable=blacklist_var
)
blacklist_checkbox.pack()

upload_date_var = tk.BooleanVar(value=True)
upload_date_checkbox = ttk.Checkbutton(
    main_frame, text="Upload Date Check", variable=upload_date_var
)
upload_date_checkbox.pack()

duration_var = tk.BooleanVar(value=True)
duration_checkbox = ttk.Checkbutton(
    main_frame, text="Duration Check", variable=duration_var
)
duration_checkbox.pack()

fuzzy_var = tk.BooleanVar(value=True)
fuzzy_checkbox = ttk.Checkbutton(main_frame, text="Fuzzy Check", variable=fuzzy_var)
fuzzy_checkbox.pack()

uploader_occurrence_var = tk.BooleanVar(value=True)
uploader_occurrence_checkbox = ttk.Checkbutton(
    main_frame, text="Uploader Occurrence Check", variable=uploader_occurrence_var
)
uploader_occurrence_checkbox.pack()

uploader_diversity_var = tk.BooleanVar(value=True)
uploader_diversity_checkbox = ttk.Checkbutton(
    main_frame, text="Uploader Diversity Check", variable=uploader_diversity_var
)
uploader_diversity_checkbox.pack()

run_button = ttk.Button(main_frame, text="Run Checks", command=run_checks)
run_button.pack()

csv_editor = CSVEditor(main_frame)  # Editor main frame
csv_editor.pack()
root.mainloop()
