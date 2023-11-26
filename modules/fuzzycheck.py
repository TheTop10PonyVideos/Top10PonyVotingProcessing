import csv
from modules import data_pulling
from fuzzywuzzy import fuzz
import re

output_file = "outputs/processedfuzzlist.csv"
input_file = "outputs/processed.csv"
titles_file = "modules/csv/datalink.csv"
SIMILARITY_THRESHOLD = 80  # Fuzzy threshhold (currently 80%)


def links_to_titles(input):
    with open(input, "r", encoding="utf-8") as csv_in, open(
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
                if "youtube.com" in cell or "youtu.be" in cell:
                    video_id = data_pulling.extract_video_id(cell)

                    if video_id:
                        title, uploader, duration, date = data_pulling.ytAPI(video_id)

                        new_row_titles[index] = title
                        new_row_uploaders[index] = uploader
                        new_row_durations[index] = duration
                else:
                    if (
                        "pony.tube" in cell
                        or "vimeo.com" in cell
                        or "dailymotion.com" in cell
                    ):
                        video_link = cell

                        if video_link:
                            (
                                title,
                                uploader,
                                duration,
                                date,
                            ) = data_pulling.check_withYtDlp(video_link=video_link)

                            new_row_titles[index] = title
                            new_row_uploaders[index] = uploader
                            new_row_durations[index] = duration

            writer_titles.writerow(new_row_titles)
            writer_uploaders.writerow(new_row_uploaders)
            writer_durations.writerow(new_row_durations)


output_titles = "outputs/titles_output.csv"
output_uploaders = "outputs/uploaders_output.csv"
output_durations = "outputs/durations_output.csv"


def adapt_output_csv(
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

    with open(output_csv_file, "w", newline="", encoding="utf-8") as output_file:
        output_writer = csv.writer(output_file)

        for i, existing_row in enumerate(existing_rows):
            adapted_row = []
            for j, cell in enumerate(existing_row):
                if (
                    (i, j) in adaptations_titles
                    and (i, j) in adaptations_uploaders
                    and (i, j) in adaptations_durations
                ):
                    adapted_row.append(
                        cell
                        + f" [SIMILARITY DETECTED IN TITLES AND UPLOADER AND DURATION]"
                    )
                elif (i, j) in adaptations_titles and (i, j) in adaptations_uploaders:
                    adapted_row.append(
                        cell + f" [SIMILARITY DETECTED IN TITLES AND UPLOADERS]"
                    )
                elif (i, j) in adaptations_titles and (i, j) in adaptations_durations:
                    adapted_row.append(
                        cell + f" [SIMILARITY DETECTED IN TITLES AND DURATION]"
                    )
                elif (i, j) in adaptations_uploaders and (
                    i,
                    j,
                ) in adaptations_durations:
                    adapted_row.append(
                        cell + f" [SIMILARITY DETECTED IN UPLOADER AND DURATION]"
                    )
                elif (i, j) in adaptations_titles:
                    adapted_row.append(cell + f" [SIMILARITY DETECTED IN TITLES]")
                elif (i, j) in adaptations_uploaders:
                    adapted_row.append(cell + f" [SIMILARITY DETECTED IN UPLOADER]")
                elif (i, j) in adaptations_durations:
                    adapted_row.append(cell + f" [SIMILARITY DETECTED IN DURATION]")
                else:
                    adapted_row.append(cell)
            output_writer.writerow(adapted_row)


date_time_pattern = r"\d{1,2}\/\d{1,2}\/\d{4} \d{1,2}:\d{1,2}:\d{1,2}"


def is_date_time_match(cell):
    return bool(re.search(date_time_pattern, cell))


def delete_first_cell():
    with open(input_file, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        rows = []

        for row in reader:
            if row and is_date_time_match(row[0]):
                rows.append(row[1:])
            else:
                rows.append(row)

    with open(input_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    print(
        f"First cell deleted from each row if it was a date and saved to {output_file}"
    )
