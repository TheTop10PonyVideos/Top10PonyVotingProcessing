import tkinter as tk
from tkinter import ttk
from modules import duplicate
from modules import blacklist
from modules import durationcheck
import os

def run_checks():
    #if duplicate_check_var.get():
    duplicate.checkDuplicates()
    #if blacklist_check_var.get():
    blacklist.checkBlacklist()
    #if duration_check_var.get():
    durationcheck.checkDuration()

    
    if os.path.exists("outputs/processedblacklist.csv"):
        os.remove("outputs/processedblacklist.csv")
    if os.path.exists("outputs/processedduplicates.csv"):
        os.remove("outputs/processedduplicates.csv")


root = tk.Tk()
root.title("Check Script")

#duplicate_check_var = tk.IntVar()
#duplicate_check = ttk.Checkbutton(root, text="Duplicate Check", variable=duplicate_check_var)
#duplicate_check.pack()

#blacklist_check_var = tk.IntVar()
#blacklist_check = ttk.Checkbutton(root, text="Blacklist Check", variable=blacklist_check_var)
#blacklist_check.pack()

#duration_check_var = tk.IntVar()
#duration_check = ttk.Checkbutton(root, text="Duration Check", variable=duration_check_var)
#duration_check.pack()

run_button = ttk.Button(root, text="Run Checks", command=run_checks)
run_button.pack()

root.mainloop()