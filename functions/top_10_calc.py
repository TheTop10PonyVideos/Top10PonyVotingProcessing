"""Functions for calculating video rankings based on number of votes."""
import csv

urls_file = "outputs/shifted_cells.csv"


def analyze_and_write_titles_to_csv(input_file: str, output_file: str):
    """Given an input CSV file containing rows of ballot data, count up the
    number of occurrences of each video voted for, and write a CSV containing
    the results sorted by number of votes.

    The input CSV should be a processed votes CSV with a layout similar to the
    following:
    
    Timestamp,,,,,,,,,,,,,,,,,,,,,
    4/1/2024 0:11:59,,Title A,,Title B, ... ,Title J,
    4/1/2024 0:11:59,,Title K,,Title L, ... ,Title T,
    ...

    """
    # TODO: Separate the CSV file operations and processing logic
    total_rows = 0
    title_counts = {}
    title_urls = {}

    with open(input_file, "r", encoding="utf-8") as titles_csv:
        with open(urls_file, "r", encoding="utf-8") as urls_csv:
            titles_reader = csv.reader(titles_csv)
            urls_reader = csv.reader(urls_csv)

            next(titles_reader)  # Skip the header row
            next(urls_reader)  # Skip the header row

            for titles_row, urls_row in zip(titles_reader, urls_reader):
                # Check if any non-empty cell exists in the row
                if any(
                    cell.strip() for cell in titles_row[1:]
                ):  # Skip the first column
                    total_rows += 1

                titles_row = titles_row[
                    2::2
                ]  # Skip the first column and odd-indexed columns
                urls_row = urls_row[
                    2::2
                ]  # Skip the first column and odd-indexed columns

                for title, url in zip(titles_row, urls_row):
                    title = title.strip()
                    url = url.strip()
                    if title:
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

