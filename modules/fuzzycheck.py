import csv
from modules import data_pulling
from fuzzywuzzy import fuzz

output_file = "outputs/processedfuzzlist.csv"
input_file = "outputs/processed.csv"
titles_file = "modules/csv/datalinks.csv"
SIMILARITY_THRESHOLD = 80  # Fuzzy threshhold (currently 80%)


def linksToTitles():  # converts all the links into titles bc we need it :P
    with open(titles_file, "r", encoding="utf-8") as csv_in, open(
        output_file, "w", newline="", encoding="utf-8"
    ) as csv_out:
        reader = csv.reader(csv_in)
        writer = csv.writer(csv_out)

        for row in reader:
            new_row = row

            for index, cell in enumerate(row):
                if "youtube.com" in cell or "youtu.be" in cell:
                    video_id = data_pulling.extract_video_id(cell)

                    if video_id:
                        title, uploader, duration = data_pulling.ytAPI(video_id)

                        new_row[index] = title
                else:
                    if (
                        "pony.tube" in cell
                        or "vimeo.com" in cell
                        or "dailymotion.com" in cell
                    ):
                        video_link = cell

                        if video_link:
                            title, uploader, duration = data_pulling.check_withYtDlp(
                                video_link=video_link
                            )

                            new_row[index] = title
            writer.writerow(new_row)


fuzzcsv = "outputs/processedfuzzlist.csv"


def adapt_output_csv(
    input_csv_file=fuzzcsv, output_csv_file=input_file
):  # checks for similar items in the processed fuzzlist and writes them into the main file.
    with open(input_csv_file, "r", encoding="utf-8") as input_file:
        input_reader = csv.reader(input_file)
        input_rows = [row for row in input_reader]

    with open(output_csv_file, "r", encoding="utf-8") as existing_file:
        existing_reader = csv.reader(existing_file)
        existing_rows = [row for row in existing_reader]

    adaptations = {}

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
                    adaptations[(i, j)] = (input_row[j], similarity)
                    adaptations[(i, k)] = (input_row[k], similarity)

    with open(output_csv_file, "w", newline="", encoding="utf-8") as output_file:
        output_writer = csv.writer(output_file)

        for i, existing_row in enumerate(existing_rows):
            adapted_row = []
            for j, cell in enumerate(existing_row):
                if (i, j) in adaptations:
                    adapted_row.append(
                        cell + f" [SIMILARITY DETECTED]"
                    )  # this is not a prince reference thanks
                else:
                    adapted_row.append(cell)
            output_writer.writerow(adapted_row)
