import csv

input_titles_path = "outputs/temp_outputs/titles_output.csv"
urls_file = "outputs/shifted_cells.csv"
output_titles_path = "outputs/calculated_top_10.csv"

# Sorts videos by comparing the titles


def analyze_and_write_titles_to_csv(input_file, output_file=output_titles_path):
    total_rows = 0
    title_counts = {}
    title_urls = {}

    with open(input_file, "r", encoding="utf-8") as titles_csv:
        with open(urls_file, "r", encoding="utf-8") as urls_csv:
            titles_reader = csv.reader(titles_csv)
            urls_reader = csv.reader(urls_csv)

            next(titles_reader)
            next(urls_reader)

            for titles_row, urls_row in zip(titles_reader, urls_reader):
                for title, url in zip(titles_row[1:], urls_row[1:]):
                    title = title.strip()
                    url = url.strip()
                    if title:
                        total_rows += 1
                        title_counts[title] = title_counts.get(title, 0) + 1
                        title_urls[title] = url

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
        csvwriter.writerow(["Title", "Percentage", "Total Votes", "URL"])

        for title, percentage in sorted_titles:
            total_votes = title_counts[title]
            url = title_urls.get(title, "")
            csvwriter.writerow([title, f"{percentage:.4f}%", total_votes, url])
