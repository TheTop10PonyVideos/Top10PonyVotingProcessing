from functions.messages import suc, inf, err

class ConsolePrinter:
    """Prints messages to the console."""

    def print(self, text: str, msg_type: str='inf'):
        """Print a message to the console.

        `msg_type` controls the appearance and coloring of the message in the
        console. Allowed values are "suc" (success messages), "inf"
        (informational messages), and "err" (error messages). Default is "inf".
        """
        if msg_type == 'suc': 
            suc(text)
        elif msg_type == 'err':
            err(text)
        else:
            inf(text)
