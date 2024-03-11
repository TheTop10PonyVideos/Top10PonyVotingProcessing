import csv

def shift_rows(rows: list[list[str]]) -> list[list[str]]:
    """Given a list of rows of string values, return a list in which each cell
    of each row is succeeded by an empty cell.
    """
    shifted_rows = []
    for row in rows:
        shifted_row = []
        for cell in row:
            shifted_row.extend([cell, ''])
        shifted_rows.append(shifted_row)

    return shifted_rows

def add_empty_cells(input_file_path: str, output_file_path: str):
    """Given an input CSV file name and an output CSV file name, read in the
    input CSV, and output a CSV with an empty column to the right of each input
    column.
    """
    with (
        open(input_file_path, "r") as input_file,
        open(output_file_path, "w", newline="") as output_file
    ):
        reader = csv.reader(input_file)
        writer = csv.writer(output_file)

        rows = [row for row in reader]
        shifted_rows = shift_rows(rows)
        writer.writerows(shifted_rows)
