import tkinter as tk

from tkinter.font import Font
from tkinter import ttk
from classes.gui import GUI

from core_utilities import (
    post_processing,
    vote_processing,
    top_10_calculator,
    archive_checker
)

post_processing.PostProcessing()
vote_processing.VoteProcessing()
top_10_calculator.Top10Calculator()
archive_checker.ArchiveStatusChecker()


class MainMenu(GUI):
    def gui(self, root):
        root.title("Top 10 Pony Videos: Main Menu")
        root.geometry(f'{800}x{400}')

        # Create main frame
        main_frame = tk.Frame(root)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Create buttons bar
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack()

        label_font = Font(size=10)

        text_label = ttk.Label(buttons_frame, text="Select a Process:", font=label_font)
        text_label.grid(column=0, row=0)

        btn_vote_processing = ttk.Button(buttons_frame, text="Vote Processing", command=lambda: GUI.run("VoteProcessing", root))
        btn_vote_processing.grid(column=0, row=1, padx=5, pady=5)

        btn_top_10_calculator = ttk.Button(buttons_frame, text="Top 10 Calculator", command=lambda: GUI.run("Top10Calculator", root))
        btn_top_10_calculator.grid(column=1, row=1, padx=5, pady=5)

        btn_post_processing = ttk.Button(buttons_frame, text="Post Processing", command=lambda: GUI.run("PostProcessing", root))
        btn_post_processing.grid(column=2, row=1, padx=5, pady=5)

        btn_archive_checker = ttk.Button(buttons_frame, text="Archive Status Checker", command=lambda: GUI.run("ArchiveStatusChecker", root))
        btn_archive_checker.grid(column=3, row=1, padx=5, pady=5)

root = tk.Tk()

GUI.run(MainMenu().__class__.__name__, root)

root.mainloop()