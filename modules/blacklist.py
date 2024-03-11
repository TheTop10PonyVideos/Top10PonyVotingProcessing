"""Blacklist check."""

import csv, os
from modules import data_pulling


def check_blacklist(video_urls_file_path: str, titles_file_path: str, output_file_path: str):
    """Given an input file containing video URLs, check the uploader of each URL
    against a blacklist. For each URL found to be blacklisted, annotate the cell
    to its right with a note indicating its blacklisted status.
    """
    temp_output_file_path = "outputs/temp_outputs/processed_blacklist.csv"

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
            for index, cell in enumerate(row_video_urls):
                if cell not in urls_to_metadata:
                    continue

                metadata = urls_to_metadata[cell]
                
                if data_pulling.check_blacklisted_channels(metadata.uploader):
                    row_titles[index + 1] += "[BLACKLISTED]"

            writer.writerow(row_titles)

    os.remove(output_file_path)
    os.rename(temp_output_file_path, output_file_path)
