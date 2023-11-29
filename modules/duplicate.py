import csv

csv_file = "modules/csv/data_link.csv"
output_file = "outputs/processedduplicates.csv"
additional_file_path = "outputs/titles_output.csv"


def mark_duplicate_cells(row, additional_row):
    seen = set()
    for i in range(len(row)):
        cell = row[i]
        if cell and cell in seen:
            additional_row[i] += " [Duplicate Video]"
        seen.add(cell)
    return additional_row


def check_duplicates(input_file):
    with open(input_file, "r", newline="", encoding="utf-8") as file, open(
        additional_file_path, "r", newline="", encoding="utf-8"
    ) as additional_file:
        reader = csv.reader(file)
        additional_reader = csv.reader(additional_file)
        rows = list(reader)
        additional_rows = list(additional_reader)

    for i in range(len(rows)):
        additional_rows[i] = mark_duplicate_cells(rows[i], additional_rows[i])

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(additional_rows)

    print(f"Duplicates marked and saved to {output_file}")
