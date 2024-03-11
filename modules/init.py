import csv


def add_empty_cells(input_file, output_file="outputs/shifted_cells.csv"):
    with open(input_file, "r") as file:
        with open(output_file, "w", newline="") as new_file:
            reader = csv.reader(file)
            writer = csv.writer(new_file)
            for row in reader:
                new_row = []
                for cell in row:
                    new_row.extend(
                        [cell, ""]
                    )  # Adds an empty cell after each content cell
                writer.writerow(new_row)
