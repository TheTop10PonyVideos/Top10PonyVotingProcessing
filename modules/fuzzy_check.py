import csv
from modules import data_pulling
from fuzzywuzzy import fuzz
import re

output_file = "outputs/temp_outputs/processed_fuzzlist.csv"
input_file = "outputs/temp_outputs/processed.csv"
titles_file = "modules/csv/data_link.csv"
SIMILARITY_THRESHOLD = 80  # Fuzzy threshhold (currently 80%)

# Checks for similarities in Titles, Uploaders and Video Length.


def links_to_titles(input):  # Converts links to titles using Google API or yt_dlp
    with open(input, "r", encoding="utf-8") as csv_in, open(  # Opens relevant files
        output_titles, "w", newline="", encoding="utf-8"
    ) as csv_out_titles, open(
        output_uploaders, "w", newline="", encoding="utf-8"
    ) as csv_out_uploaders, open(
        output_durations, "w", newline="", encoding="utf-8"
    ) as csv_out_durations:
        reader = csv.reader(csv_in)
        writer_titles = csv.writer(csv_out_titles)
        writer_uploaders = csv.writer(csv_out_uploaders)
        writer_durations = csv.writer(csv_out_durations)

        for row in reader:
            new_row_titles = row.copy()
            new_row_uploaders = row.copy()
            new_row_durations = row.copy()

            for index, cell in enumerate(row):
                if (
                    "youtube.com" in cell or "youtu.be" in cell
                ):  # Checks youtube with the Google API
                    video_id = data_pulling.extract_video_id(cell)

                    if video_id:
                        title, uploader, duration, date = data_pulling.yt_api(video_id)

                        new_row_titles[index] = title
                        new_row_uploaders[index] = uploader
                        new_row_durations[index] = duration
                else:
                    if data_pulling.contains_accepted_domain(
                        cell
                    ):  # Checks for other links comparing to the accepted_domains.csv file
                        video_link = cell

                        if video_link:
                            (
                                title,
                                uploader,
                                duration,
                                date,
                            ) = data_pulling.check_with_yt_dlp(video_link=video_link)

                            new_row_titles[index] = title
                            new_row_uploaders[index] = uploader
                            new_row_durations[index] = duration

            writer_titles.writerow(new_row_titles)
            writer_uploaders.writerow(new_row_uploaders)
            writer_durations.writerow(new_row_durations)


output_titles = "outputs/temp_outputs/titles_output.csv"
output_uploaders = "outputs/temp_outputs/uploaders_output.csv"
output_durations = "outputs/temp_outputs/durations_output.csv"


def fuzzy_match(
    input_csv_file=output_titles,
    output_csv_file=input_file,
    uploader_csv_file=output_uploaders,
    duration_csv_file=output_durations,
):
    with open(input_csv_file, "r", encoding="utf-8") as input_file:
        input_reader = csv.reader(input_file)
        input_rows = [row for row in input_reader]

    with open(output_csv_file, "r", encoding="utf-8") as existing_file:
        existing_reader = csv.reader(existing_file)
        existing_rows = [row for row in existing_reader]

    with open(uploader_csv_file, "r", encoding="utf-8") as uploader_file:
        uploader_reader = csv.reader(uploader_file)
        uploader_rows = [row for row in uploader_reader]
    with open(duration_csv_file, "r", encoding="utf-8") as duration_file:
        duration_reader = csv.reader(duration_file)
        duration_rows = [row for row in duration_reader]

    adaptations_titles = {}
    adaptations_uploaders = {}
    adaptations_durations = {}

    # Check for similarities in titles
    for i, (input_row, existing_row) in enumerate(zip(input_rows, existing_rows)):
        for j in range(1, len(input_row)):
            if not input_row[j]:
                continue

            for k in range(j + 1, len(input_row)):
                if not input_row[k]:
                    continue

                similarity = fuzz.ratio(input_row[j], input_row[k])
                if similarity >= SIMILARITY_THRESHOLD:
                    print(
                        f"Similarity in row {i+1} between titles {j} and {k}: {similarity}%"
                    )
                    adaptations_titles[(i, j)] = (input_row[j], similarity)
                    adaptations_titles[(i, k)] = (input_row[k], similarity)

    # Check for similarities in uploaders
    for i, (input_row, existing_row) in enumerate(zip(uploader_rows, existing_rows)):
        for j in range(1, len(input_row)):
            if not input_row[j]:
                continue

            for k in range(j + 1, len(input_row)):
                if not input_row[k]:
                    continue

                similarity = fuzz.ratio(input_row[j], input_row[k])
                if similarity >= SIMILARITY_THRESHOLD:
                    print(
                        f"Similarity in row {i+1} between uploaders {j} and {k}: {similarity}%"
                    )
                    adaptations_uploaders[(i, j)] = (input_row[j], similarity)
                    adaptations_uploaders[(i, k)] = (input_row[k], similarity)

    for i, (input_row, existing_row) in enumerate(zip(duration_rows, existing_rows)):
        for j in range(1, len(input_row)):
            if not input_row[j]:
                continue

            for k in range(j + 1, len(input_row)):
                if not input_row[k]:
                    continue

                similarity = fuzz.ratio(input_row[j], input_row[k])
                if similarity >= SIMILARITY_THRESHOLD:
                    print(
                        f"Similarity in row {i+1} between duration {j} and {k}: {similarity}%"
                    )
                    adaptations_durations[(i, j)] = (input_row[j], similarity)
                    adaptations_durations[(i, k)] = (input_row[k], similarity)

    with open(
        "outputs/processed.csv", "w", newline="", encoding="utf-8"
    ) as output_file:
        output_writer = csv.writer(output_file)

        for i, existing_row in enumerate(existing_rows):
            for j, cell in enumerate(existing_row):
                similarity_note = None  # Initialize to None if no similarity detected

                if (
                    (i, j) in adaptations_titles
                    and (i, j) in adaptations_uploaders
                    and (i, j) in adaptations_durations
                ):
                    similarity_note = (
                        f" [SIMILARITY DETECTED IN TITLES AND UPLOADER AND DURATION]"
                    )
                elif (i, j) in adaptations_titles and (i, j) in adaptations_uploaders:
                    similarity_note = f" [SIMILARITY DETECTED IN TITLES AND UPLOADERS]"
                elif (i, j) in adaptations_titles and (i, j) in adaptations_durations:
                    similarity_note = f" [SIMILARITY DETECTED IN TITLES AND DURATION]"
                elif (i, j) in adaptations_uploaders and (
                    i,
                    j,
                ) in adaptations_durations:
                    similarity_note = f" [SIMILARITY DETECTED IN UPLOADER AND DURATION]"
                elif (i, j) in adaptations_titles:
                    similarity_note = f" [SIMILARITY DETECTED IN TITLES]"
                elif (i, j) in adaptations_uploaders:
                    similarity_note = f" [SIMILARITY DETECTED IN UPLOADER]"

                if similarity_note is not None:
                    existing_row[
                        j + 1
                    ] += similarity_note  # Add the similarity note to the next cell

            output_writer.writerow(
                existing_row
            )  # Write the modified row to the output file
