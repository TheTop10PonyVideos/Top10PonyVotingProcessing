import csv


def count_occurrences(values: list) -> dict:
    """Given a list of values, return a dictionary containing a count of the
    occurrences of each value.
    """
    occurrences = {}
    for value in values:
        occurrences[value] = occurrences.get(value, 0) + 1

    return occurrences


def get_uploaders_from_row(row: list[str]) -> list[str]:
    """Given a row of string values, return every nonempty row other than the
    first and last. For the uploaders CSV, this should provide a list of all
    the uploader cells.
    """
    return [uploader.strip() for uploader in row[1:-1] if uploader.strip()]


def check_uploader_occurrence(
    uploaders_file_path: str, titles_file_path: str, output_file_path: str
):
    """Check the names of all uploaders for every submission. If a particular
    uploader shows up 3 times or more in a submission, the note "[DUPLICATE
    CREATOR]" is appended to the notes column of every video uploaded by the
    duplicate creator in `processed.csv`.
    """

    with (
        open(uploaders_file_path, "r", encoding="utf-8") as csv_uploaders,
        open(titles_file_path, "r", encoding="utf-8") as csv_titles,
    ):
        reader_uploaders = csv.reader(csv_uploaders)
        reader_titles = csv.reader(csv_titles)

        rows_uploaders = list(reader_uploaders)
        rows_titles = list(reader_titles)

        for line_number, row in enumerate(rows_uploaders, start=1):
            # Extract uploader names from the row
            uploaders = get_uploaders_from_row(row)

            # Count the occurrences of each uploader
            uploader_count = count_occurrences(uploaders)

            for uploader, count in uploader_count.items():
                # For each uploader
                if count >= 3:
                    # If this uploader appears 3 times or more
                    for i in range(2, len(row)):
                        # For each cell
                        if rows_uploaders[line_number - 1][i] == uploader:
                            # If this cell in uploaders_output.csv is the duplicate creator
                            rows_titles[line_number - 1][i + 1] += "[DUPLICATE CREATOR]"
                            # Append note to notes column for corresponding cell in processed.csv

    # Write to processed.csv
    with open(
        titles_file_path, "w", newline="", encoding="utf-8"
    ) as processed_uploaders_csv:
        writer = csv.writer(processed_uploaders_csv)
        writer.writerows(rows_titles)
