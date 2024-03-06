import csv
from modules import data_pulling
import re
import os
import shutil

input_file_duration = "modules/csv/data_link.csv"
input_file_additional_info = "outputs/temp_outputs/processed.csv"
output_file = "outputs/temp_outputs/processed_duration.csv"

# Checks for length


def check_duration(input):
    with open(input, "r", encoding="utf-8") as csv_data_link, open(  # Checks CSV
        input_file_additional_info, "r", encoding="utf-8"
    ) as csv_blacklist, open(output_file, "w", newline="", encoding="utf-8") as csv_out:
        reader_data_link = csv.reader(csv_data_link)
        reader_durations = csv.reader(csv_blacklist)
        writer = csv.writer(csv_out)

        for row_data_link, row_duration in zip(reader_data_link, reader_durations):
            new_row = row_data_link

            for index, cell in enumerate(row_data_link[2:]):
                if index % 2 == 0:  # Process every other cell
                    if index // 2 < len(row_data_link):
                        link = row_data_link[index // 2]
                if (
                    "youtube.com" in cell or "youtu.be" in cell
                ):  # Checks youtube with the Google API
                    video_id = data_pulling.extract_video_id(cell)

                    if video_id:
                        (
                            title,
                            uploader,
                            duration,
                            upload_date_str,
                        ) = data_pulling.yt_api(video_id)

                        if int(duration):
                            seconds = int(duration)
                        else:
                            print(
                                "[DURATION CHECK] ERROR NO VIDEO DATA PROCEEDING WITH '0'"
                            )
                            continue

                        if (
                            seconds <= 30
                        ):  # Checks videos for possible for possible or definite duration problem
                            row_duration[index + 3] += "[VIDEO TOO SHORT]"

                        elif seconds <= 45:
                            row_duration[index + 3] += "[VIDEO MAYBE TOO SHORT]"

                elif data_pulling.contains_accepted_domain(
                    cell
                ):  # Checks for other links comparing to the accepted_domains.csv file
                    video_link = cell

                    if video_link:
                        print(video_link)
                        (
                            title,
                            uploader,
                            duration,
                            upload_date_str,
                        ) = data_pulling.check_with_yt_dlp(video_link=video_link)
                        seconds = int(duration)

                        if (
                            seconds <= 30
                        ):  # Checks videos for possible for possible or definite duration problem
                            row_duration[index + 3] += "[VIDEO TOO SHORT]"

                        elif seconds <= 45:
                            row_duration[index + 3] += "[VIDEO MAYBE TOO SHORT]"
                elif cell.strip():
                    if index < len(row_duration):
                        row_duration[index + 3] += "[UNSUPPORTED HOST]"

            writer.writerow(row_duration)
    os.remove("outputs/temp_outputs/processed.csv")
    os.rename(output_file, "outputs/temp_outputs/processed.csv")
