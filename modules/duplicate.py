"""Duplicate check."""

import csv

additional_file_path = "outputs/temp_outputs/titles_output.csv"
output_file = "outputs/temp_outputs/processed.csv"


def mark_duplicate_cells(row: list[str], additional_row: list[str]) -> list[str]:
    """Given a row of string values, check for identical values in the same row;
    for each duplicated value found (not including the first), find the cell
    with the same index in an additional input row, and annotate the cell to its
    right to indicate the duplicate.
    """
    seen = set()
    for i in range(len(row)):
        cell = row[i]
        if cell and cell in seen:
            additional_row[i + 1] += "[DUPLICATE VIDEO]"
        seen.add(cell)
    return additional_row


def check_duplicates(input_file: str):
    """Check the given CSV file for duplicate entries."""
    with (
        open(input_file, "r", newline="", encoding="utf-8") as file,
        open(
            additional_file_path, "r", newline="", encoding="utf-8"
        ) as additional_file,
    ):
        reader = csv.reader(file)
        additional_reader = csv.reader(additional_file)

        rows = list(reader)
        additional_rows = list(additional_reader)

    for i in range(len(rows)):  # Calls the marking function
        additional_rows[i] = mark_duplicate_cells(rows[i], additional_rows[i])

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(additional_rows)

    print(f"Duplicates marked and saved to {output_file}")
