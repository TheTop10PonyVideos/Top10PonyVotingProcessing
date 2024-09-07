import tkinter as tk

from PIL import Image, ImageTk, ImageSequence
from tkinter.font import Font
from tkinter import ttk
from classes.gui import GUI
import math

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
    def __init__(self, max_frame_rate, rate_deriv):
        super().__init__()
        self.gif_playing = False
        self.i_frame = 0
        self.max_frame_rate = max_frame_rate
        self.rate_deriv = rate_deriv
        self.frame_incr_time = self.time_till_next_frame(0, self.get_next_frame_rate(0))
        self.next_fps = 0
        self.t = self.frame_incr_time

    
    def gui(self, root):
        root.title("Top 10 Pony Videos: Main Menu")
        root.geometry(f'{800}x{400}')

        self.gif_frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(Image.open("images/ttpvp.gif"))]
        self.gif_label = tk.Label(root, image=self.gif_frames[self.i_frame])
        self.gif_label.pack()

        self.gif_label.bind("<Enter>", self.start_gif)
        self.gif_label.bind("<Leave>", self.stop_gif)

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
    

    def start_gif(self, event):
        if not self.gif_playing:
            self.gif_playing = True
            self.rate_deriv = abs(self.rate_deriv)
            self.next_fps = self.get_next_fps()
            root.after(int(1000 * self.frame_incr_time), self.play_gif)
        elif self.rate_deriv < 0:
            self.rate_deriv *= -1

    # Note: no idea why, but the frame rate seems to be capped by tkinter
    # Moving the mouse over the window seems to show an increased fps past the cap
    # it for whatever reason, as well as having more than one recursive loop of play_gif
    def play_gif(self):
        if self.next_fps < 0 or self != GUI.active_gui:
            self.next_fps = 0
            self.gif_playing = False  
            return
          
        self.i_frame = (self.i_frame + 1) % len(self.gif_frames)
        self.gif_label.config(image=self.gif_frames[self.i_frame])

        self.frame_incr_time = 1 / min(
            1 / self.time_till_next_frame(self.next_fps, self.get_next_frame_rate(self.next_fps)),
            self.max_frame_rate
        )

        self.next_fps = min(self.get_next_fps(), self.max_frame_rate)

        root.after(int(1000 * self.frame_incr_time), self.play_gif)


    def stop_gif(self, event):
        self.rate_deriv = -1 * abs(self.rate_deriv)

    # UAM equations were used to derive the following methods
    def get_next_frame_rate(self, rate_initial):
        val_to_root = rate_initial * rate_initial + 2 * self.rate_deriv
        modif = (1 - 2 * (val_to_root < 0))
        return modif * math.sqrt(modif * val_to_root)


    def time_till_next_frame(self, rate_initial, rate_final):
        return (rate_final - rate_initial) / self.rate_deriv
    

    def get_next_fps(self):
        val_to_root = self.next_fps * self.next_fps + 2 * self.rate_deriv
        modif = (1 - 2 * (val_to_root < 0))
        return modif * math.sqrt(modif * val_to_root)



root = tk.Tk()

GUI.run(MainMenu(100, 100).__class__.__name__, root)

root.mainloop()