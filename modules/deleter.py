import csv

input_file = "outputs/processed.csv"
output_file = "outputs/processedAutomated.csv"
values_to_remove = [
    "[SIMILARITY DETECTED]",
    "[Video to Short]",
    "[Duplicate Video]",
    "[BLACKLISTED]",
]


def deleteEntries():
    with open(input_file, "r") as infile, open(output_file, "w", newline="") as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        for row in reader:
            new_row = []
            for cell in row:
                if all(value not in cell for value in values_to_remove):
                    new_row.append(cell)
            writer.writerow(new_row)


# This script is deleting all cells with notes. Just ignore it you will get your regular untouched output anyways.
