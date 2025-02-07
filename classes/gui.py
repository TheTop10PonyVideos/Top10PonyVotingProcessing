import tkinter as tk, dotenv, os
from PIL import Image, ImageTk

dotenv.load_dotenv()

class GUI:
    root = tk.Tk()
    instances = {}
    active_gui = None
    _key_image = None
    _var_yt_api_key = None
    _frame_api_key = None
    
    # Allows guis to use other GUI instances by their class names
    # Otherwise would leave the circular imports issue with the main menu
    def __init__(self):
        GUI.instances[self.__class__.__name__] = self

        # ready should be used if a gui's background task tries modifying its widgets
        # or when it takes a while for the widgets to load such as when waiting for web responses
        self.ready = False

    # Named gui to be more intuitive when overriding rather than in its use in this class
    def gui(self, root: tk.Tk):
        """Code to build the gui should override this method.

        NOTE: Some variables may be garbage collected after the gui is built,
        so if anything appears to be missing, try saving its variable to self.
        """

    @staticmethod
    def _toggle_key_entry():
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
        """Clears the current window and builds the gui from the provided class name into it"""

        if GUI.active_gui:
            GUI.active_gui.ready = False

            for widget in GUI.root.winfo_children():
                widget.destroy()

        GUI.active_gui = GUI.instances[gui_name]

        GUI.active_gui.ready = False
        GUI.active_gui.gui(GUI.root)

        if not GUI._key_image:
            GUI._key_image = ImageTk.PhotoImage(
                Image.open("images/key.png").resize((30, 30))
            )
            GUI._var_yt_api_key = tk.StringVar()

        tk.Button(
            GUI.root,
            padx=5,
            pady=5,
            image=GUI._key_image,
            command=lambda: GUI._toggle_key_entry(),
        ).place(relx=0.95, rely=0.95, anchor="se")

        GUI.active_gui.ready = True
    
    @staticmethod
    def get_api_key() -> str | None:
        """Get the Youtube API key from the key entry box or, if not present,
        from the .env file. Failure to find a key results in a message box
        prompting the user to input a key"""

        youtube_api_key = GUI._var_yt_api_key.get().strip()

        if not youtube_api_key:
            youtube_api_key = os.getenv("apikey", "").strip()

        if not youtube_api_key:
            tk.messagebox.showinfo("Error", "Please provide a Youtube API key.")

        return youtube_api_key
