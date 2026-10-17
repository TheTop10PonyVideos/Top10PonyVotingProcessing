import tkinter as tk
from PIL import Image, ImageTk
from threading import Thread
import asyncio, dotenv

dotenv.load_dotenv()

class GUI:
    """Base user interface class."""
    # Static Tk instance which is started in main.py and runs until the
    # application exits. All GUI subclasses construct their interfaces inside
    # this instance.
    root = tk.Tk()

    # Static dictionary that gets populated with each instance of a GUI subclass
    # when they are initialized. This allows GUI instances to reference each
    # other via this dictionary.
    instances = {}

    # Stores the GUI currently being shown to the user.
    _active_gui = None

    _key_image = None
    _frame_api_key = None
    _var_yt_api_key = tk.StringVar()

    # The asyncio event loop that will run all tasks in the same background thread
    task_loop = asyncio.new_event_loop()

    # Allows guis to use other GUI instances by their class names
    # Otherwise would leave the circular imports issue with the main menu
    def __init__(self):
        self.name = self.__class__.__name__
        GUI.instances[self.name] = self
        self._tasks = set()

    # Named gui to be more intuitive when overriding rather than in its use in this class
    def gui(self, root: tk.Tk):
        """Method for building the gui.

        NOTE: Some items like ImageTk.PhotoImage may be garbage collected when building the gui,
        so if anything appears to be missing, try saving them to self.
        """

    def gui_update(self) -> bool:
        """Method for updating the ui content every few milliseconds,
        using values computed from `task()` which runs in a separate thread."""

    def before(self):
        """Method for updating the ui just before starting a `task()`'s update loop
        starts in a separate thread."""

    def finish(self):
        """Method for making a final ui render, ran after a task completes and the view hasn't changed."""

    @staticmethod
    def _toggle_key_entry():
        """Handler for the "YT API Key" button, which appears on all GUI windows
        as a key icon in the bottom-right corner."""
        if GUI._frame_api_key is not None and GUI._frame_api_key.winfo_exists():
            return GUI._frame_api_key.destroy()

        GUI._frame_api_key = tk.Frame(GUI.root)
        GUI._frame_api_key.place(relx=0.9, rely=0.95, anchor="se")
        tk.Label(GUI._frame_api_key, text="YT API Key:").grid(row=0, column=0)
        tk.Entry(
            GUI._frame_api_key, textvariable=GUI._var_yt_api_key, width=15, show="*"
        ).grid(row=1, column=0)

    @staticmethod
    def run(gui_name: str):
        """Clear the current window and build the gui from the provided class
        name into it."""

        # Decommission the current active GUI and destroy it.
        if GUI._active_gui:
            for widget in GUI.root.winfo_children():
                widget.destroy()

        # Switch the active GUI to the new instance.
        GUI._active_gui: GUI = GUI.instances[gui_name]

        GUI._active_gui.gui(GUI.root)

        # Add the YT API Key field toggle button.
        if not GUI._key_image:
            GUI._key_image = ImageTk.PhotoImage(
                Image.open("images/key.png").resize((30, 30))
            )

        tk.Button(
            GUI.root,
            padx=5,
            pady=5,
            image=GUI._key_image,
            command=lambda: GUI._toggle_key_entry(),
        ).place(relx=0.95, rely=0.95, anchor="se")

        if GUI._active_gui.tasks_running():
            GUI._active_gui.before()
            GUI._active_gui._update_loop()

    def _update_loop(self):
        # Stop ui content updates when the view changes
        if self.name != GUI._active_gui.name:
            return

        completed = not self.tasks_running()
        self.gui_update()

        if completed:
            self.finish()
        else:
            GUI.root.after(15, self._update_loop)

    def tasks_running(self):
        """Returns the number of tasks running for the current GUI view"""
        return len(self._tasks)

def _start_loop():
    asyncio.set_event_loop(GUI.task_loop)
    GUI.task_loop.run_forever()

GUI.task_thread = Thread(target=_start_loop, daemon=True).start()
