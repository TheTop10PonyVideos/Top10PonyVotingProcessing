"""Functions for outputting messages to the standard error output stream in the
console. Uses ANSI escape codes to add more distinctive coloring for different
types of messages.
"""

import sys
import logging


logger = logging.getLogger()
logging.basicConfig(filename="outputs/TT10PVP.log", filemode="w", level=logging.INFO)


def print_stderr(*args, **kwargs):
    """Print to stderr."""
    print(*args, file=sys.stderr, **kwargs)


def suc(text: str):
    """Print success message to stderr."""
    print_stderr(f"\033[1;32m+++ {text}\033[0;0m")
    logger.info(text)


def inf(text: str):
    """Print info message to stderr."""
    print_stderr(f"\033[1;33m>>> {text}\033[0;0m")
    logger.info(text)


def err(text: str):
    """Print error message to stderr."""
    print_stderr(f"\033[1;31m!!! {text}\033[0;0m")
    logger.info(text)
