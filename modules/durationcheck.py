import csv
from modules import data_pulling
import re

input_file_duration = "modules/csv/datalink.csv"
input_file_additional_info = "outputs/processedDates.csv"
output_file = "outputs/processed.csv"
date_time_pattern = r"\d{1,2}\/\d{1,2}\/\d{4} \d{1,2}:\d{1,2}:\d{1,2}"


def is_date_time_match(cell):
    return bool(re.search(date_time_pattern, cell))


def checkDuration(input):
    with open(input, "r", encoding="utf-8") as csv_duration, open(
        input_file_additional_info, "r", encoding="utf-8"
    ) as csv_additional, open(
        output_file, "w", newline="", encoding="utf-8"
    ) as csv_out:
        reader_duration = csv.reader(csv_duration)
        reader_additional = csv.reader(csv_additional)
        writer = csv.writer(csv_out)

        for row_duration, row_additional in zip(reader_duration, reader_additional):
            new_row = row_duration

            for index, cell in enumerate(row_duration):
                if "youtube.com" in cell or "youtu.be" in cell:
                    video_id = data_pulling.extract_video_id(cell)

                    if video_id:
                        title, uploader, duration, date = data_pulling.ytAPI(video_id)

                        seconds = int(duration)

                        if seconds <= 30:
                            row_additional[index] = cell + " [Video too short]"
                        elif seconds <= 45:
                            row_additional[index] = cell + "[Check Video Length!]"
                else:
                    if (
                        "pony.tube" in cell
                        or "vimeo.com" in cell
                        or "dailymotion.com" in cell
                    ):
                        video_link = cell

                        if video_link:
                            print(video_link)
                            (
                                title,
                                uploader,
                                duration,
                                date,
                            ) = data_pulling.check_withYtDlp(video_link=video_link)

                            seconds = int(duration)

                            if seconds <= 30:
                                row_additional[index] = cell + " [Video too short]"
                            elif seconds <= 45:
                                row_additional[index] = cell + "[Check Video Length!]"
                    else:
                        if cell.strip():
                            if is_date_time_match(cell):
                                row_additional.pop(index)
                            else:
                                if index < len(row_additional):
                                    row_additional[index] = cell + "[Unsupported Host]"
                                else:
                                    row_additional.append(cell + "[Unsupported Host]")

            writer.writerow(row_additional)
