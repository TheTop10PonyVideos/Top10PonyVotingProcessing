import csv

csv_file = "modules/csv/datalink.csv"
output_file = "outputs/processedduplicates.csv"


def markDuplicateCells(row):
    seen = set()
    for i in range(len(row)):
        cell = row[i]
        if cell and cell in seen:
            row[i] += " [Duplicate Video]"
        seen.add(cell)
    return row


def checkDuplicates(input):
    with open(input, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        rows = list(reader)

    for i in range(len(rows)):
        rows[i] = markDuplicateCells(rows[i])

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print(f"Duplicates marked and saved to {output_file}")
