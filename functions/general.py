"""General-use functions."""

from random import randint
from pathlib import Path
import pandas as pd


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


def pad_csv_rows(df: pd.DataFrame, num_rows: int):
    """Given a dataframe of string columns, return the same
    structure but padded with empty rows to the given amount. For example,
    padding a 5-row CSV to 10 rows will append 5 empty rows. An empty row is a
    list of zero-length strings.

    If the given list of rows is already greater than the desired pad length, it
    is returned unchanged."""
    num_rows_diff = len(df) - num_rows

    # No padding required
    if len(df) >= num_rows:
        return df

    # Pad with empty rows 
    empty_rows = pd.DataFrame('', index=range(num_rows_diff), columns=df.columns)
    padded_rows = pd.concat([df, empty_rows], ignore_index=True)

    return padded_rows
