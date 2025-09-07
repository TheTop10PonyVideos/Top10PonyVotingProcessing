"""General-use functions."""

import csv, requests, os
from functions.messages import suc, inf
from random import randint
from pathlib import Path
from classes.typing import ArchiveRecord
from data.globals import (
    honorable_mentions_csv_url,
    local_honorable_mentions_csv_path,
    local_top_10_archive_csv_path,
    top_10_archive_csv_url
)


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
 

def load_top_10_master_archive(local_first = True) -> list[ArchiveRecord]:
    """Load a copy of the Top 10 Pony Videos List spreadsheet. Load a local copy if local_first is True,
    or if there's no such copy on the filesystem, export one from Google Sheets and
    save it first.

    The archive is returned as a list of records, with the key names being the
    field headers of the master archive file."""

    archive_records = None
    while True:
        try:
            if not local_first:
                local_first = True
                raise Exception

            # Try to load the local copy of the master archive spreadsheet
            with Path(local_top_10_archive_csv_path).open(
                "r", encoding="utf-8"
            ) as file:
                inf("Loading local copy of master Top 10 Pony Videos archive...")
                reader = csv.DictReader(file)
                reader.fieldnames = [field_name.lower().replace(" ", "_") for field_name in reader.fieldnames]
                archive_records = [record for record in reader]
                break
        except Exception:
            inf(
                "Downloading a copy of the master Top 10 Pony Videos archive..."
            )
            response = requests.get(top_10_archive_csv_url)
            response.encoding = "utf-8"
            Path(local_top_10_archive_csv_path).write_text(
                response.text, encoding="utf-8"
            )
            suc(
                f"Local copy of master Top 10 Pony Videos archive saved to {local_top_10_archive_csv_path}."
            )

    return archive_records


def load_honorable_mentions_archive(local_first = True) -> list[ArchiveRecord]:
    """Load a copy of the honorable mentions spreadsheet. Load a local copy if local_first is True,
    or if there's no local copy on the filesystem, export one from Google Sheets and
    save it first.

    The archive is returned as a list of records, with the key names being the
    same field headers of the master archive file."""

    archive_records = None
    while True:
        try:
            if not local_first:
                local_first = True
                raise Exception

            # Try to load the local copy of the honorable mentions archive spreadsheet
            with Path(local_honorable_mentions_csv_path).open(
                "r", encoding="utf-8"
            ) as file:
                inf("Loading local copy of honorable mentions archive...")
                reader = csv.DictReader(file)
                reader.fieldnames[reader.fieldnames.index("Original Link")] = "link"
                reader.fieldnames = [field_name.lower().replace(" ", "_") for field_name in reader.fieldnames]
                archive_records = [record for record in reader]
                break
        except Exception:
            inf(
                "Downloading a copy of the honorable mentions archive one..."
            )
            response = requests.get(honorable_mentions_csv_url)
            response.encoding = "utf-8"
            Path(local_honorable_mentions_csv_path).write_text(
                response.text, encoding="utf-8"
            )
            suc(
                f"Local copy of honorable mentions archive saved to {local_honorable_mentions_csv_path}."
            )

    return archive_records
