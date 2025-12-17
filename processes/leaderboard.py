"""
Leaderboard - 12 Month Rolling: https://docs.google.com/spreadsheets/d/1E7-TBbrIGJ2tPAbWaRnhDRk0QJvZlZtfEAteCjXTxfs/edit?usp=sharing

=QUERY(
  ImportedData!A2:L121,
  "select Col6, sum(Col12)*100, count(Col12)
   where Col6 is not null
   group by Col6
   order by sum(Col12)*100 desc
   label sum(Col12)*100 'Sum', count(Col12) 'Count'",
  0
)

Currently using this to import data from the master list and look at the past 120 entries to represent 12 months.

Is there a better way to do this? Ideally, a way to compare different months and see changes over time for commentary purposes would be useful.
"""
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.font import Font
from PIL import ImageTk, Image
from classes.gui import GUI

class Leaderboard(GUI):
    def __init__(self):
        super().__init__()

    def gui(self, root):
        # Create application window
        root.title("Top 10 Pony Videos: Leaderboard")
        root.geometry("800x600")

        # Create main frame
        main_frame = tk.Frame(root)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Single-column grid layout
        main_frame.columnconfigure(0, weight=1)

        # Create banner image
        self.banner_image = ImageTk.PhotoImage(Image.open("images/leaderboard.png"))
        banner_label = tk.Label(main_frame, image=self.banner_image)
        banner_label.grid(row=0, column=0)

        # Create title
        title_font = Font(size=16)
        title_label = tk.Label(main_frame, font=title_font, text="Leaderboard")
        title_label.grid(row=1, column=0, pady=8)

        # Create scrollable leaderboard
        board_frame = tk.Frame(main_frame)
        board_frame.grid(row=2, column=0, padx=5, pady=5)

        # Add quit button
        quit_button = ttk.Button(
            main_frame,
            text="Back to Main Menu",
            command=lambda: GUI.run("MainMenu"),
        )
        quit_button.grid(row=3, column=0, padx=5, pady=5)

    def show_archive(self):
        master_archive = load_top_10_master_archive()
