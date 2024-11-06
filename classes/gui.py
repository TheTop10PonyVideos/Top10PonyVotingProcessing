import tkinter as tk
from PIL import Image, ImageTk


class GUI:
    instances = {}
    active_gui = None
    _key_image = None
    yt_api_key_var = None
    _key_frame = None

    # Allows guis to use other GUI instances by their class names
    # Mainly made to circumvent circular imports with the main menu
    def __init__(self):
        GUI.instances[self.__class__.__name__] = self
        self._yt_api_key_entry = None
        # ready should be used if a gui's background task tries modifying its widgets
        # or when it takes a while for the widgets to load such as when waiting for web responses
        self.ready = False

    # Named gui to be more intuitive when overriding rather than in its use in this class
    def gui(self, root: tk.Tk):
        """Code to build the gui should override this method.

        NOTE: Some variables may be garbage collected after the gui is built,
        so if anything appears to be missing, try saving its variable to self.
        """
        pass

    @staticmethod
    def _toggle_key_entry(root):
        if GUI._key_frame is not None and GUI._key_frame.winfo_exists():
            return GUI._key_frame.destroy()

        GUI._key_frame = tk.Frame(root)
        GUI._key_frame.place(relx=0.9, rely=0.95, anchor="se")
        tk.Label(GUI._key_frame, text="YT API Key:").grid(row=0, column=0)
        tk.Entry(
            GUI._key_frame, textvariable=GUI.yt_api_key_var, width=15, show="*"
        ).grid(row=1, column=0)

    @staticmethod
    def run(gui_name: str, root: tk.Tk):
        """Clears the current window and builds the gui from the provided class name into it"""

        if GUI.active_gui:
            GUI.active_gui.ready = False

            for widget in root.winfo_children():
                widget.destroy()

        GUI.active_gui = GUI.instances[gui_name]

        GUI.active_gui.ready = False
        GUI.active_gui.gui(root)

        if not GUI._key_image:
            GUI._key_image = ImageTk.PhotoImage(
                Image.open("images/key.png").resize((30, 30))
            )
            GUI.yt_api_key_var = tk.StringVar()

        tk.Button(
            root,
            padx=5,
            pady=5,
            image=GUI._key_image,
            command=lambda: GUI._toggle_key_entry(root),
        ).place(relx=0.95, rely=0.95, anchor="se")

        GUI.active_gui.ready = True
