from tkinter import Tk

class GUI():
    instances = {}
    active_gui = None
    
    # Allows guis to use other GUI instances by their class names
    # Mainly made to circumvent circular imports with the main menu
    def __init__(self):
        GUI.instances[self.__class__.__name__] = self
        # ready should be used if a gui's background task tries modifying its widgets
        # or when it takes a while for the widgets to load such as when waiting for web responses
        self.ready = False

    # Named gui to be more intuitive when overriding rather than in its use in this class
    def gui(self, root: Tk):
        """Code to build the gui should override this method\n
        Note: Some variables may be garbage collected after the gui is built,
        so if anything appears to be missing try saving its variable to self"""
        pass

    @staticmethod
    def run(gui_name: str, root: Tk):
        """Clears the current window and builds the gui from the provided class name into it"""
        
        if GUI.active_gui:
            GUI.active_gui.ready = False

            for widget in root.winfo_children():
                widget.destroy()

        GUI.active_gui = GUI.instances[gui_name]

        GUI.active_gui.ready = False
        GUI.active_gui.gui(root)
        GUI.active_gui.ready = True