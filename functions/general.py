"""General-use functions."""

from random import randint
from pathlib import Path


def load_text_data(path_str: str) -> list[str]:
    """Given a file containing lines of text, return an array containing the
    contents of each line. Empty lines and lines containing only whitespace are
    ignored. The file data is expected to be in UTF-8 format and will be decoded
    as such."""

    path = Path(path_str)
    with path.open("r", encoding="utf-8") as file:
        lines = [line for line in file if line.strip() != ""]
        lines = [line.strip("\n") for line in lines]
        return lines


def get_freq_table(values: list) -> dict:
    """Given a list of values, return a dictionary mapping each value to the
    number of times it occurs in the list."""

    freqs = {}

    for value in values:
        if value not in freqs:
            freqs[value] = 0
        freqs[value] += 1

    return freqs


def sample_item_without_replacement(items: list):
    """Given a list of items, sample one random item, remove it from the list,
    and return the item."""
    if len(items) == 0:
        raise ValueError("Cannot sample from empty list")

    random_index = randint(0, len(items) - 1)
    sampled_item = items[random_index]
    del items[random_index]

    return sampled_item
