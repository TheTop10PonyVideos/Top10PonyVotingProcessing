import tkinter as tk
from tkinter import ttk, filedialog
from calculation import calc
import os


def browse_file():  # Function that asks for a CSV file
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    entry_var.set(file_path)


def run_checks():
    csv = entry_var.get()
    calc.analyze_and_write_titles_to_csv(csv)


# This still breaks if you don't enable all checks
root = tk.Tk()  # Creating the GUI
root.title("Calc Script")

entry_var = tk.StringVar()
entry = ttk.Entry(root, textvariable=entry_var)
entry.pack(padx=10, pady=10)


browse_button = ttk.Button(root, text="Browse", command=browse_file)
browse_button.pack(pady=10)

run_button = ttk.Button(root, text="Run Checks", command=run_checks)
run_button.pack()

root.mainloop()
