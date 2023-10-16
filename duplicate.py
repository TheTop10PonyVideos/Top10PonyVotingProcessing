import csv

csv_file = "data.csv"
output_file = "data_with_duplicates.csv"


def has_duplicates(row):
    seen = set()
    for item in row:
        if item and item in seen:
            return True
        seen.add(item)
    return False


with open(csv_file, "r", newline="", encoding="utf-8") as file:
    reader = csv.reader(file)
    rows = list(reader)
for row in rows:
    if has_duplicates(row[1:]):
        row[0] += ", Duplicate"
with open(output_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(rows)
print(f"Duplicates marked and saved to {output_file}")
