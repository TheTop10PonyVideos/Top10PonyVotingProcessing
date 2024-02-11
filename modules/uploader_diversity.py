import csv

input_file_path = "outputs/temp_outputs/uploaders_output.csv"
# input_file_path = "outputs/temp_outputs/test_input_delete.csv"
output_file_path = "outputs/processed.csv"
# output_file_path = "outputs/processed_test_delete.csv"


def check_uploader_diversity():
    # Checks the names of all uploaders within every submission.
    # If a submission contains < 5 unique uploaders, each cell of
    # the submission in processed.csv is flagged with the "[DUPLICATE CREATOR]"
    # tag to signify that the entire submission is invalidated.
    with open(input_file_path, "r", newline="", encoding="utf-8") as input_file, open(
        output_file_path, "r+", newline="", encoding="utf-8"
    ) as output_file:
        uploader_reader = csv.reader(input_file)
        uploader_rows = list(uploader_reader)
        processed_reader = csv.reader(output_file)
        processed_rows = list(processed_reader)
        processed_writer = csv.writer(output_file)

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
                    if processed_rows[line_number][cell_number] != "":
                        # If current cell is not empty
                        processed_rows[line_number][cell_number] += " [5 CHANNEL RULE]"
                        # Append note to cell

        output_file.seek(0)
        processed_writer.writerows(processed_rows)
