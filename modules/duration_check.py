import csv
from modules import data_pulling
import re
import os
import shutil


def evaluate_video_duration(seconds: int) -> str:
    """Evaluate the given duration and return one of the following numeric
    codes:

    0 = acceptable length
    1 = too short
    2 = maybe too short
    """

    if seconds <= 30:
        return 1
    elif seconds <= 45:
        return 2

    return 0


def check_duration(
    video_urls_file_path: str, titles_file_path: str, output_file_path: str
):
    temp_output_file_path = "outputs/temp_outputs/processed_duration.csv"

    with (
        open(video_urls_file_path, "r", encoding="utf-8") as csv_video_urls,
        open(titles_file_path, "r", encoding="utf-8") as csv_titles,
        open(temp_output_file_path, "w", newline="", encoding="utf-8") as csv_output,
    ):
        reader_video_urls = csv.reader(csv_video_urls)
        reader_titles = csv.reader(csv_titles)
        writer = csv.writer(csv_output)

        rows_video_urls = [row for row in reader_video_urls]

        urls = []
        for row in rows_video_urls:
            urls.extend(data_pulling.get_video_urls(row))

        urls_to_metadata = data_pulling.get_urls_to_metadata(urls)

        for row_video_urls, row_titles in zip(rows_video_urls, reader_titles):
            for index, cell in enumerate(row_video_urls[2:]):
                if cell.strip() == "":
                    continue

                duration_check_label = "[UNSUPPORTED HOST]"

                if cell in urls_to_metadata:
                    seconds = urls_to_metadata[cell].duration
                    duration_check_result = evaluate_video_duration(seconds)

                    if duration_check_result == 0:
                        continue

                    duration_check_labels = {
                        1: "[VIDEO TOO SHORT]",
                        2: "[VIDEO MAYBE TOO SHORT]",
                    }

                    duration_check_label = duration_check_labels[duration_check_result]

                row_titles[index + 3] += duration_check_label

            writer.writerow(row_titles)

    os.remove(output_file_path)
    os.rename(temp_output_file_path, output_file_path)
