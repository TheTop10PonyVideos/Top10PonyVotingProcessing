"""Fuzzy matching functions. Checks for similarities in Titles, Uploaders and
Video Length to identify potential duplicate videos.
"""
import csv, re
from modules import data_pulling
from fuzzywuzzy import fuzz

# This file is used as the input to the fuzzy check. It should, at the point the
# fuzzy check is made, contain the set of URLs uploaded by the user, with an
# annotation column to the right of each URL column.
input_file = "outputs/temp_outputs/processed.csv"

# Fuzzy threshold percentage
SIMILARITY_THRESHOLD = 80


def links_to_titles(input_file_name: str):
    """Given a CSV file containing video URLs, output 3 new CSV files in which
    each URL is replaced by the video title, uploader, and duration
    respectively. The video metadata is obtained via a lookup to the Google API
    or yt-dlp.

    The 3 output CSV files are specified by setting the global variables
    `output_titles`, `output_uploaders`, and `output_durations`.
    """
    with (
        open(input_file_name, "r", encoding="utf-8") as csv_in,
        open(output_titles, "w", newline="", encoding="utf-8") as csv_out_titles,
        open(output_uploaders, "w", newline="", encoding="utf-8") as csv_out_uploaders,
        open(output_durations, "w", newline="", encoding="utf-8") as csv_out_durations
    ):
        reader = csv.reader(csv_in)
        writer_titles = csv.writer(csv_out_titles)
        writer_uploaders = csv.writer(csv_out_uploaders)
        writer_durations = csv.writer(csv_out_durations)

        for row in reader:
            new_row_titles = row.copy()
            new_row_uploaders = row.copy()
            new_row_durations = row.copy()

            for index, cell in enumerate(row):
                # For YouTube videos, use the YouTube Data API to obtain video
                # metadata.
                if "youtube.com" in cell or "youtu.be" in cell:
                    video_id = data_pulling.extract_video_id(cell)

                    if video_id:
                        title, uploader, duration, date = data_pulling.yt_api(video_id)
                        if title and uploader and duration:

                            new_row_titles[index] = title
                            new_row_uploaders[index] = uploader
                            new_row_durations[index] = duration
                        else:
                            print(f'ERROR: Could not obtain video data from YouTube Data API for video id {video_id}. Marking video as private.')
                            new_row_titles[index] = "VIDEO PRIVATE"
                            new_row_uploaders[index] = "VIDEO PRIVATE"
                            new_row_durations[index] = "VIDEO PRIVATE"

                # For non-YouTube videos, attempt to obtain metadata via yt-dlp.
                # The application only permits videos from whitelisted domains;
                # these are defined in `accepted_domains.csv`.
                elif data_pulling.contains_accepted_domain(cell):
                    video_link = cell

                    if video_link:
                        title, uploader, duration, date = data_pulling.check_with_yt_dlp(video_link=video_link)
                        if title and uploader and duration:
                            new_row_titles[index] = title
                            new_row_uploaders[index] = uploader
                            new_row_durations[index] = duration
                        else:
                            print(f'ERROR: Could not obtain video data via yt-dlp for video id {video_id}. Marking video as private.')
                            new_row_titles[index] = "VIDEO PRIVATE"
                            new_row_uploaders[index] = "VIDEO PRIVATE"
                            # TODO: This isn't consistent with the treatment for the YouTube Data API above. Should it be 0 or "VIDEO PRIVATE"?
                            new_row_durations[index] = 0

            writer_titles.writerow(new_row_titles)
            writer_uploaders.writerow(new_row_uploaders)
            writer_durations.writerow(new_row_durations)


output_titles = "outputs/temp_outputs/titles_output.csv"
output_uploaders = "outputs/temp_outputs/uploaders_output.csv"
output_durations = "outputs/temp_outputs/durations_output.csv"

def check_similar_values(values: list[str], similarity_threshold: int, start_offset: int = 0) -> list:
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
        if values[i] == '':
            continue
        for j in range(i+1, len(values)):
            if values[j] == '':
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

    for row_index, row  in enumerate(rows):
        similar_values = check_similar_values(row, SIMILARITY_THRESHOLD, 1)

        for col_index_a, col_index_b, similarity in similar_values:
            print(
                f"Similarity in row {row_index+1} between columns {col_index_a+1} and {col_index_b+1}: {similarity}%"
            )
            similarities[(row_index, col_index_a)] = (row[col_index_a], similarity)
            similarities[(row_index, col_index_b)] = (row[col_index_b], similarity)

    return similarities


def fuzzy_match(
    output_csv_filename=input_file,
    titles_csv_filename=output_titles,
    uploader_csv_filename=output_uploaders,
    duration_csv_filename=output_durations
):
    """Given an input CSV file containing video URLs, and 3 CSV files containing
    corresponding titles, uploaders, and durations for each cell in the input
    CSV, check each of those 3 CSV files for similar entries in each row; then,
    for each cell of the input CSV, update the cell to its right with
    annotations describing the categories in which it is similar to other cells.
    Write the resulting CSV to `outputs/processed.csv`.
    """

    csv_file_names = {
        'titles': titles_csv_filename,
        'uploader': uploader_csv_filename,
        'duration': duration_csv_filename,
        'existing': output_csv_filename
    }

    rows = {}
    for category, csv_file_name in csv_file_names.items():
        with open(csv_file_name, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            rows[category] = [row for row in reader]

    category_order = ['titles', 'uploader', 'duration']

    adaptations = {category: check_similarities(rows[category]) for category in category_order}

    with open("outputs/processed.csv", "w", newline="", encoding="utf-8") as output_file:
        output_writer = csv.writer(output_file)

        for i, existing_row in enumerate(rows['existing']):
            for j, cell in enumerate(existing_row):
                cell_coord = (i, j)

                # Get the list of categories for which the given cell was found to be similar to other cells in its row.
                adaptations_containing_cell = [
                    category.upper() for category in category_order if cell_coord in adaptations[category]
                ]

                if len(adaptations_containing_cell) > 0:
                    similarity_note = f"[SIMILARITY DETECTED IN {' AND '.join(adaptations_containing_cell)}]"

                    # Add the similarity note to the next cell
                    existing_row[j + 1] += similarity_note

            # Write the modified row to the output file
            output_writer.writerow(existing_row)
