import csv

input_titles_path = "outputs/temp_outputs/titles_output.csv"
output_titles_path = "outputs/calculated_top_10.csv"

# Sorts videos by comparing the titles


def analyze_and_write_titles_to_csv(input_file, output_file=output_titles_path):
    total_rows = 0
    title_counts = {}

    with open(input_file, "r", encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        for row in csvreader:
            if any(field.strip() for field in row):
                total_rows += 1
                for index, title_value in enumerate(row[2:], start=1):
                    if index % 2 != 0 and title_value.strip():
                        title_counts[title_value] = title_counts.get(title_value, 0) + 1

    title_percentage = {  # calculates percentage
        title: (count / total_rows) * 100 for title, count in title_counts.items()
    }

    sorted_titles = sorted(  # sort counts based on percentage
        title_percentage.items(),
        key=lambda x: x[1],
        reverse=True,
    )  # Sorts titles by percentage

    with open(
        output_file, "w", newline="", encoding="utf-8"
    ) as csvfile:  # writes rows to the output
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Title", "Percentage", "Total Votes"])

        for title, percentage in sorted_titles:
            total_votes = title_counts[title]
            csvwriter.writerow([title, f"{percentage:.4f}%", total_votes])
