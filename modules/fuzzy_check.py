"""Fuzzy matching functions. Checks for similarities in Titles, Uploaders and
Video Length to identify potential duplicate videos.
"""

import csv, re
from modules import data_pulling
from fuzzywuzzy import fuzz

# Fuzzy threshold percentage
SIMILARITY_THRESHOLD = 80


def check_similar_values(
    values: list[str], similarity_threshold: int, start_offset: int = 0
) -> list:
    """Given a list of string values, return a list of tuples (i, j, s), where i
    and j are the indices of two values that are considered to be "similar",
    and s is their similarity percentage. The similarity metric is the
    Levenshtein distance, calculated by the fuzzywuzzy library.

    If `start_offset` is given, values with indices lower than that will not be
    considered in the similarity check (ie. use `start_offset=1` to skip the
    first value).
    """

    similar_values = []

    for i in range(start_offset, len(values)):
        if values[i] == "":
            continue
        for j in range(i + 1, len(values)):
            if values[j] == "":
                continue
            similarity = fuzz.ratio(values[i], values[j])
            if similarity >= similarity_threshold:
                similar_values.append((i, j, similarity))

    return similar_values


def check_similarities(rows: list[str]) -> dict[tuple[int, int], tuple[str, float]]:
    """Check each row in `rows` for similarities, and return a dictionary
    mapping (r, c) tuples to (v, s) tuples, where

        r = row index
        c = column index
        v = cell value
        s = similarity percentage

    The first column is not included in the similarity check. Cells that are
    below the similarity threshold are not included in the results.
    """

    similarities = {}

    for row_index, row in enumerate(rows):
        similar_values = check_similar_values(row, SIMILARITY_THRESHOLD, 1)

        for col_index_a, col_index_b, similarity in similar_values:
            print(
                f"Similarity in row {row_index+1} between columns {col_index_a+1} and {col_index_b+1}: {similarity}%"
            )
            similarities[(row_index, col_index_a)] = (row[col_index_a], similarity)
            similarities[(row_index, col_index_b)] = (row[col_index_b], similarity)

    return similarities


def links_to_titles(
    video_urls_file_path: str,
    output_titles_file_name: str,
    output_uploaders_file_name: str,
    output_durations_file_name: str,
):
    """Given a CSV file containing video URLs, output 3 new CSV files in which
    each URL is replaced by the video title, uploader, and duration
    respectively. The video metadata is obtained via a lookup to the YouTube
    Data API or to yt-dlp.

    The 3 output CSV files are specified by setting the global variables
    `output_titles`, `output_uploaders`, and `output_durations`.
    """
    with (
        open(video_urls_file_path, "r", encoding="utf-8") as csv_video_urls,
        open(
            output_titles_file_name, "w", newline="", encoding="utf-8"
        ) as csv_out_titles,
        open(
            output_uploaders_file_name, "w", newline="", encoding="utf-8"
        ) as csv_out_uploaders,
        open(
            output_durations_file_name, "w", newline="", encoding="utf-8"
        ) as csv_out_durations,
    ):
        reader = csv.reader(csv_video_urls)
        writer_titles = csv.writer(csv_out_titles)
        writer_uploaders = csv.writer(csv_out_uploaders)
        writer_durations = csv.writer(csv_out_durations)

        rows = [row for row in reader]

        urls = []
        for row in rows:
            urls.extend(data_pulling.get_video_urls(row))

        urls_to_metadata = data_pulling.get_urls_to_metadata(urls)

        for row in rows:
            new_row_titles = row.copy()
            new_row_uploaders = row.copy()
            new_row_durations = row.copy()

            for index, cell in enumerate(row):
                if cell not in urls_to_metadata:
                    continue

                metadata = urls_to_metadata[cell]

                if metadata.title and metadata.uploader and metadata.duration:
                    new_row_titles[index] = metadata.title
                    new_row_uploaders[index] = metadata.uploader
                    new_row_durations[index] = metadata.duration
                else:
                    if data_pulling.is_youtube_link(cell):
                        # If we weren't able to get title/uploader/duration
                        # information for a YouTube video, leave the cell
                        # unchanged in the output (ie. keep it as a URL).
                        print(
                            f"ERROR: Could not obtain video data from YouTube Data API for {cell}."
                        )
                        new_row_titles[index] = cell
                        new_row_uploaders[index] = cell
                        new_row_durations[index] = cell
                    else:
                        # If we weren't able to get title/uploader/duration
                        # information for a non-YouTube video, set the title to
                        # "VIDEO PRIVATE".
                        #
                        # TODO: This isn't consistent with the treatment for the
                        # YouTube Data API above. Shouldn't the URLs be kept for
                        # non-YouTube videos too?
                        print(
                            f"ERROR: Could not obtain video data via yt-dlp for video id {video_id}. Marking video as private."
                        )
                        new_row_titles[index] = "VIDEO PRIVATE"
                        new_row_uploaders[index] = "VIDEO PRIVATE"
                        new_row_durations[index] = 0

            writer_titles.writerow(new_row_titles)
            writer_uploaders.writerow(new_row_uploaders)
            writer_durations.writerow(new_row_durations)


def fuzzy_match(
    output_csv_filename: str,
    titles_csv_filename: str,
    uploader_csv_filename: str,
    duration_csv_filename: str,
):
    """Given an input CSV file containing video URLs, and 3 CSV files containing
    corresponding titles, uploaders, and durations for each cell in the input
    CSV, check each of those 3 CSV files for similar entries in each row; then,
    for each cell of the input CSV, update the cell to its right with
    annotations describing the categories in which it is similar to other cells.
    Write the resulting CSV to `outputs/processed.csv`.
    """

    csv_file_names = {
        "titles": titles_csv_filename,
        "uploader": uploader_csv_filename,
        "duration": duration_csv_filename,
        "existing": output_csv_filename,
    }

    rows = {}
    for category, csv_file_name in csv_file_names.items():
        with open(csv_file_name, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            rows[category] = [row for row in reader]

    category_order = ["titles", "uploader", "duration"]

    adaptations = {
        category: check_similarities(rows[category]) for category in category_order
    }

    with open(
        "outputs/processed.csv", "w", newline="", encoding="utf-8"
    ) as output_file:
        output_writer = csv.writer(output_file)

        for i, existing_row in enumerate(rows["existing"]):
            for j, cell in enumerate(existing_row):
                cell_coord = (i, j)

                # Get the list of categories for which the given cell was found to be similar to other cells in its row.
                adaptations_containing_cell = [
                    category.upper()
                    for category in category_order
                    if cell_coord in adaptations[category]
                ]

                if len(adaptations_containing_cell) > 0:
                    similarity_note = f"[SIMILARITY DETECTED IN {' AND '.join(adaptations_containing_cell)}]"

                    # Add the similarity note to the next cell
                    existing_row[j + 1] += similarity_note

            # Write the modified row to the output file
            output_writer.writerow(existing_row)
