import csv

titles_file = "modules/csv/data_link.csv"
output_titles = "outputs/titles_output.csv"
output_file = "outputs/processed_titles.csv"
input_titles_path = "outputs/titles_output.csv"
output_titles_path = "outputs/calculated_top_10.csv"

# Sorts videos by comparing the titles


def analyze_and_write_titles_to_csv(input_file, output_file=output_titles_path):
    title_counts = {}
    total_title_count = 0

    with open(
        input_file, "r", encoding="utf-8"
    ) as csvfile:  # Opens the CSV and checks number of votes for every title
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            for title_value in row:
                if title_value.strip():
                    title_counts[title_value] = title_counts.get(title_value, 0) + 1
                    total_title_count += 1

            total_title_count -= 1

    title_percentage = {
        title: (count / total_title_count) * 100
        for title, count in title_counts.items()
    }

    sorted_titles = sorted(
        title_percentage.items(),
        key=lambda x: x[1],
        reverse=True,
    )  # Sorts votes accordingly

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Title", "Percentage"])  # Writes results to the output CSV

        for title, percentage in sorted_titles:
            csvwriter.writerow([title, f"{percentage:.4f}%"])
