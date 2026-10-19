import asyncio
import os
import tkinter as tk
from classes.gui import GUI
from typing import Callable


def get_api_key():
    """Get the Youtube API key from the key entry box or, if not present,
    from the .env file. Failure to find a key results in a message box
    prompting the user to input a key"""

    key = GUI._var_yt_api_key.get().strip()

    if not key:
        key = os.getenv("apikey", "")

    if not key or key == "YOUR_API_KEY":
        tk.messagebox.showinfo("Error", "Please provide a Youtube API key.")

    return key


def browse_file_csv(entry_var: tk.StringVar, saving=False):
    """Returns a handler for a "Browse" button. Opens a file dialog and sets the
    variable `entry_var` to the selected file. Whether the file to be used is for saving
    or opening, `saving` should be used to adjust what the prompt will say."""
    def handler():
        dialog = tk.filedialog.asksaveasfilename if saving else tk.filedialog.askopenfilename

        file_path = dialog(filetypes=[("CSV Files", "*.csv")])

        if not file_path:
            return entry_var.get()
        elif not file_path.endswith(".csv"):
            file_path += ".csv"

        entry_var.set(file_path)
        return file_path

    return handler


def task(async_func):
    """A long running function, or long enough to cause the window to freeze, for the current process, which will run in a
    dedicated task thread so that the GUI event loop isn't blocked."""

    def threaded(self: GUI, *args, **kwargs):
        self.before()

        future = asyncio.run_coroutine_threadsafe(async_func(self, *args, **kwargs), GUI.task_loop)

        self._tasks.add(future)
        future.add_done_callback(self._tasks.discard)

        if self.tasks_running() == 1:
            self._update_loop()

        return future

    return threaded


def message_box(title=None, message=None, buttons: list[tuple[str, Callable]] = []):
    msg_box = tk.Toplevel()
    msg_box.title(title)

    tk.Label(
        msg_box,
        text=message,
        font=('Arial', 12, 'bold'),
        wraplength=300
    ).pack(padx=30, pady=10)

    button_frame = tk.Frame(msg_box)

    for i, (button_text, button_func) in enumerate(buttons):
        tk.Button(
            button_frame,
            text=button_text,
            command=button_func
        ).grid(row=0, column=i, padx=15)

    tk.Button(button_frame, text="OK", command=msg_box.destroy).grid(row=0, column=len(buttons), padx=15)

    button_frame.pack(pady=15)
    msg_box.grab_set()
