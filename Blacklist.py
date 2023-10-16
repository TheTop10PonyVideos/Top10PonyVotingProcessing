# NOT WORKING CODE, PUSHED FOR AVAILABILITY BETWEEN DEVICES

import csv

csv_file = "data.csv"
output_file = "data_with_blacklist.csv"
Blacklist_titles = "Titles_Blacklist.csv"


def is_blacklist(row):
    seen = set()
    for item in row:
        for blacklistitem in blacklist:
            if item in blacklistitem:
                print("true", blacklistitem, item)
                return True
            seen.add(item)
    return False


with open(csv_file, "r", newline="", encoding="utf-8") as file:
    reader = csv.reader(file)
    rows = list(reader)
with open(Blacklist_titles, "r", newline="", encoding="utf-8") as file:
    reader = csv.reader(file)
    blacklist = list(reader)
for row in rows:
    if is_blacklist(row[1:]):
        row[0] += ", Blacklisted"
with open(output_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(rows)
print(f"Blacklisted marked and saved to {output_file}")
