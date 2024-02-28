import csv
from modules import data_pulling
import os

input_file_data_link = "modules/csv/data_link.csv"
input_file_processed_duplicates = "outputs/temp_outputs/processed.csv"
output_file = "outputs/temp_outputs/processed_blacklist.csv"


def check_blacklist(input):  # Check for blacklisted channels
    with open(input, "r", encoding="utf-8") as csv_data_link, open(  # Opens CSV
        input_file_processed_duplicates, "r", encoding="utf-8"
    ) as csv_duplicates, open(
        output_file, "w", newline="", encoding="utf-8"
    ) as csv_out:
        reader_data_link = csv.reader(csv_data_link)
        reader_duplicates = csv.reader(csv_duplicates)
        writer = csv.writer(csv_out)

        for row_data_link, row_duplicates in zip(reader_data_link, reader_duplicates):
            new_row = row_data_link

            for index, cell in enumerate(row_data_link):
                if index % 2 == 0:  # Process every other cell
                    if index // 2 < len(row_data_link):
                        link = row_data_link[index // 2]
                if (
                    "youtube.com" in cell or "youtu.be" in cell
                ):  # Checks youtube with the Google API
                    video_id = data_pulling.extract_video_id(cell)

                    if video_id:
                        title, uploader, seconds, upload_date_str = data_pulling.yt_api(
                            video_id
                        )
                        if data_pulling.check_blacklisted_channels(uploader):
                            row_duplicates[index + 1] += "[BLACKLISTED]"

                elif data_pulling.contains_accepted_domain(
                    cell
                ):  # Checks for other links comparing to the accepted_domains.csv file
                    video_link = cell

                    if video_link:
                        print(video_link)
                        (
                            title,
                            uploader,
                            seconds,
                            upload_date_str,
                        ) = data_pulling.check_with_yt_dlp(video_link=video_link)

                        if data_pulling.check_blacklisted_channels(uploader):
                            row_duplicates[index + 1] += "[BLACKLISTED]"

            writer.writerow(row_duplicates)
    os.remove("outputs/temp_outputs/processed.csv")
    os.rename(output_file, "outputs/temp_outputs/processed.csv")
