import csv

input_file = "outputs/temp_outputs/uploaders_output.csv"
main_file = "outputs/processed.csv"

def check_uploader_occurence():
# Checks the names of all uploaders for every submission.
# If a particular uploader shows up 3 times or more in a submission,
# the note "[DUPLICATE CREATOR]" is appended to the notes column
# of every video uploaded by the duplicate creator in processed.csv

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

            for uploader, count in uploader_count.items():
            # For each uploader
                if count >= 3:
                # If this uploader appears 3 times or more
                    for i in range(2, len(row)):
                    # For each cell
                        if (rows[line_number - 1][i] == uploader):
                        # If this cell in uploaders_output.csv is the duplicate creator
                            main_rows[line_number - 1][i + 1] += "[DUPLICATE CREATOR]"
                            # Append note to notes column for corresponding cell in processed.csv

    # Write to processed.csv
    with open(main_file, "w", newline="", encoding="utf-8") as processed_uploaders_csv:
        writer = csv.writer(processed_uploaders_csv)
        writer.writerows(main_rows)
