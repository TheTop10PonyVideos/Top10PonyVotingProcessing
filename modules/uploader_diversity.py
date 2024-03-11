import csv


with open("modules/csv/possible_notes.csv", "r") as csvfile:
    notes = []
    reader = csv.reader(csvfile)
    for row in reader:
        notes.extend(row)
    # Initialize list of notes for contains_note() check.

def contains_note(cell):
    """Return True if cell contains at least one annotation, e.g. "[DUPLICATE
    CREATOR]"
    """
    return any(domain in cell for domain in notes)


def check_uploader_diversity(uploaders_file_path: str, titles_file_path: str, output_file_path: str):
    """Check the names of all uploaders within every submission. If a submission
    contains fewer than 5 unique uploaders, every cell of the submission in
    `processed.csv` is flagged with the "[DUPLICATE CREATOR]" tag to signify
    that the entire submission is invalidated.
    """

    processed_rows = None

    with (
        open(uploaders_file_path, "r", newline="", encoding="utf-8") as uploaders_file,
        open(titles_file_path, "r+", newline="", encoding="utf-8") as titles_file
    ):

        reader_uploaders = csv.reader(uploaders_file)
        reader_titles = csv.reader(titles_file)

        uploader_rows = list(reader_uploaders)
        processed_rows = list(reader_titles)

        for line_number in range(1, len(uploader_rows)):
            # For each line in uploaders_output.csv
            uploaders = [
                uploader.strip() for uploader in uploader_rows[line_number][1:]
            ]
            uploaders = [item for item in uploaders if item]
            # Remove empty elements from list

            if len(set(uploaders)) < 5:
                # If this submission has < 5 unique uploaders
                for cell_number in range(2, len(processed_rows[line_number])):
                    # For each corresponding cell in processed.csv
                    cell = processed_rows[line_number][cell_number]
                    if cell != "" and not contains_note(cell):
                        # If cell is a video title, append note to notes column
                        processed_rows[line_number][cell_number + 1] += "[5 CHANNEL RULE]"

    with (
        open(output_file_path, "r+", newline="", encoding="utf-8") as output_file
    ):
        processed_writer = csv.writer(output_file)
        processed_writer.writerows(processed_rows)



