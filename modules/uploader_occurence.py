import csv

input_file = "outputs/temp_outputs/uploaders_output.csv"
output_file = "outputs/processed_uploaders.csv"
main_file = "outputs/processed.csve"

def check_uploader_occurence():
    invalid_submissions = []

    with open(input_file, "r", encoding="utf-8") as csvfile, open(main_file, "r", encoding="utf-8") as mainfile:
        reader = csv.reader(csvfile)
        rows = list(reader)
        mainReader = csv.reader(mainfile)
        mainRows = list(mainReader)

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
                        # Start from 1 to avoid adding tag to timestamp
                        for i in range(1, len(row)):
                            mainRows[line_number - 1][i] += " [DUPLICATE CREATOR]"

    # Write the processed data to processed_uploaders.csv
    with open(
        main_file, "w", newline="", encoding="utf-8"
    ) as processed_uploaders_csv:
        writer = csv.writer(processed_uploaders_csv)
        writer.writerows(mainRows)

    if invalid_submissions:
        print(f"Processed data written to {output_file}")
        print("Invalid submissions:")
        for line_number in invalid_submissions:
            print(
                f"Line {line_number  - 1}: [DUPLICATE CREATOR] appended to uploader names"
            )
