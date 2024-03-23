"""Functions for outputting messages to the standard error output stream in the
console. Uses ANSI escape codes to add more distinctive coloring for different
types of messages.
"""

import sys

def print_stderr(*args, **kwargs):
    """Print to stderr."""
    print(*args, file=sys.stderr, **kwargs)

def suc(text: str):
    """Print success message to stderr."""
    print_stderr(f'\033[1;32m+++ {text}\033[0;0m')

def inf(text: str):
    """Print info message to stderr."""
    print_stderr(f'\033[1;33m>>> {text}\033[0;0m')

def err(text: str):
    """Print error message to stderr."""
    print_stderr(f'\033[1;31m!!! {text}\033[0;0m')

