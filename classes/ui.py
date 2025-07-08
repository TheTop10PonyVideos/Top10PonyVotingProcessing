"""User interface classes.

TODO: The CSVEditor is deprecated and this file is no longer in use. Can be removed."""

import csv
import tkinter as tk
from tkinter import ttk, filedialog


class CSVEditor(tk.Frame):
    """CSV editor UI."""

    def __init__(self, master):
        super().__init__(master, borderwidth=1, relief="sunken")

        self.file_path = tk.StringVar()
        self.data = []

        self.create_widgets()

    def create_widgets(self):
        """Create and lay out the various UI widgets required by the CSV editor."""
        # File select button and save button
        self.buttons_frame = tk.Frame(self)
        self.load_csv_button = ttk.Button(
            self.buttons_frame, text="📁 Load CSV...", command=self.browse_file
        )
        self.save_button = ttk.Button(
            self.buttons_frame, text="💾 Save Changes", command=self.save_changes
        )
        self.load_processed_csv_button = ttk.Button(
            self.buttons_frame,
            text="📄 Load Processed CSV",
            command=self.load_processed_csv,
        )

        self.load_csv_button.grid(row=0, column=0)
        self.save_button.grid(row=0, column=1)
        self.load_processed_csv_button.grid(row=0, column=2)

        self.buttons_frame.pack(padx=10, pady=10)

        # Frame to hold the CSV data grid
        self.data_frame = tk.Frame(self)
        self.data_frame.pack(expand=True, fill="both")

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

        self.inner_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

    def browse_file(self):
        """Open a file dialog and load the selected CSV file into the editor."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.load_csv(file_path)

    def load_csv(self, file_path):
        """Load the given CSV file into the editor and update the display."""
        self.data = []
        self.file_path.set(file_path)
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.data.append(row)

        self.display_csv()

    def load_processed_csv(self):
        """Load the "processed" CSV file into the editor."""
        processed_csv_file = "outputs/processed.csv"
        self.load_csv(processed_csv_file)

    def display_csv(self):
        """Render the CSV data to the editor canvas."""
        # Clear existing widgets
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        label_colors = {
            "orange": [
                "[SIMILARITY DETECTED",
                "[DUPLICATE CREATOR]",
                "[VIDEO TOO OLD]",
                "[VIDEO TOO NEW]",
                "[VIDEO MAYBE TOO SHORT]",
                "[NOT WHITELISTED]",
            ],
            "red": [
                "[5 CHANNEL RULE]",
                "[UNSUPPORTED HOST]",
                "[VIDEO TOO SHORT]",
                "[BLACKLISTED]",
            ],
        }

        # Display CSV data
        for row_idx, row in enumerate(self.data):
            for col_idx, value in enumerate(row):
                entry = tk.Entry(self.inner_frame, width=50)
                entry.grid(row=row_idx, column=col_idx, padx=5, pady=5)
                entry.insert(tk.END, value)
                # Cell color defaults to green.
                entry_fg_color = "green"

                # Set the cell color depending on whether the cell value
                # contains (or partially contains) any of a given set of labels.
                # If a cell contains orange and red labels, red is given
                # priority.
                for label_color, labels in label_colors.items():
                    for label in labels:
                        if label in value:
                            entry_fg_color = label_color
                            break

                entry.config(fg=entry_fg_color)

    def save_changes(self):
        """Save any text changes made via the UI to the CSV file (that was
        selected by pressing the "Load CSV..." button)."""
        for row_idx, row in enumerate(self.data):
            for col_idx, _ in enumerate(row):
                entry_widget = self.inner_frame.grid_slaves(
                    row=row_idx, column=col_idx
                )[0]
                self.data[row_idx][col_idx] = entry_widget.get()

        if self.file_path.get() == "":
            tk.messagebox.showinfo(
                "Error", "No CSV file loaded. Please load a CSV file first."
            )
            return

        # Save the changes
        with open(self.file_path.get(), "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.data)
