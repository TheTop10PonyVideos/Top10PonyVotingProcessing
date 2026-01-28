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


def pad_csv_rows(rows: list[list], num_rows: int) -> list[list]:
    """Given a list of lists representing the rows of a CSV, return the same
    structure but padded with empty rows to the given amount. For example,
    padding a 5-row CSV to 10 rows will append 5 empty rows. An empty row is a
    list of zero-length strings.

    It is expected that every row will have the same length, as this is usually
    the case with CSVs produced by a spreadsheet program. If this is not the
    case, an error is thrown.

    If the given list of rows is already greater than the desired pad length, it
    is returned unchanged."""
    num_rows_diff = len(rows) - num_rows

    # No padding required
    if len(rows) >= num_rows:
        return rows

    # Raise error if all rows not same length
    row_length = len(rows[0])
    for i, row in enumerate(rows):
        if len(row) != row_length:
            raise Exception(f"Cannot pad rows - all rows must be the same length. The first row has length {row_length}, but row {i} has length {len(rows[0])}")

    # Pad with empty rows 
    padded_rows = []
    for i in range(num_rows):
        if i < len(rows):
            padded_rows.append(rows[i])
            continue

        empty_row = ["" for j in range(row_length)]
        padded_rows.append(empty_row)

    return padded_rows
