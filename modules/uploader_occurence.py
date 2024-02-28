import csv

input_file = "outputs/temp_outputs/uploaders_output.csv"
output_file = "outputs/processed_uploaders.csv"
main_file = "outputs/processed.csv"


def check_uploader_occurence():
    # Checks the names of all uploaders within every submission.
    # If a particular uploader shows up 3 times or more in a submission,
    # each cell of the submission in processed.csv is flagged with the
    # "[DUPLICATE CREATOR]" tag to signify that the entire submission is invalidated.
    invalid_submissions = []

    with open(input_file, "r", encoding="utf-8") as csvfile, open(
        main_file, "r", encoding="utf-8"
    ) as mainfile:
        reader = csv.reader(csvfile)
        rows = list(reader)
        main_reader = csv.reader(mainfile)
        main_rows = list(main_reader)

        for line_number, row in enumerate(rows, start=1):
            # Extract uploader names from the row
            uploaders = [uploader.strip() for uploader in row[1:-1] if uploader.strip()]

            # Count the occurrences of each uploader
            uploader_count = {}
            for uploader in uploaders:
                uploader_count[uploader] = uploader_count.get(uploader, 0) + 1

            # Check if any uploader appears 3 or more times
            for uploader, count in uploader_count.items():
                if count >= 3:
                    invalid_submissions.append(line_number)
                    # Append the substring to each uploader in the row
                    for i in range(2, len(row)):
                        # For each corresponding cell in processed.csv
                        cell = main_rows[line_number - 1][i]
                        if cell != "" and not contains_note(cell):
                        # If cell is a video title
                            main_rows[line_number - 1][i + 1] += "[DUPLICATE CREATOR]"
                            # Append note to notes column
                                    

    # Write the processed data to processed_uploaders.csv
    with open(main_file, "w", newline="", encoding="utf-8") as processed_uploaders_csv:
        writer = csv.writer(processed_uploaders_csv)
        writer.writerows(main_rows)

    if invalid_submissions:
        print(f"Processed data written to {output_file}")
        print("Invalid submissions:")
        for line_number in invalid_submissions:
            print(
                f"Line {line_number  - 1}: [DUPLICATE CREATOR] appended to uploader names"
            )

with open("modules/csv/possible_notes.csv", "r") as csvfile:
    notes = []
    reader = csv.reader(csvfile)
    for row in reader:
        notes.extend(row)
    # Initialize list of notes for contains_note() check.

def contains_note(cell): # Returns true if cell contains at least one note, e.g. [DUPLICATE CREATOR]
    return any(domain in cell for domain in notes)