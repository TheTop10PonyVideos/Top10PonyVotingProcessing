import csv
from modules import data_pulling

input_file = "outputs/processedblacklist.csv"
output_file = "outputs/processed.csv"


def checkDuration():
    with open(input_file, "r", encoding="utf-8") as csv_in, open(
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

                        seconds = int(duration)

                        if seconds <= 30:
                            new_row[index] = cell + " [Video to Short]"
                else:
                    if (
                        "pony.tube" in cell
                        or "vimeo.com" in cell
                        or "dailymotion.com" in cell
                    ):
                        video_link = cell

                        if video_link:
                            print(video_link)
                            title, uploader, duration = data_pulling.check_withYtDlp(
                                video_link=video_link
                            )

                            seconds = int(duration)

                            if seconds <= 30:
                                new_row[index] = cell + " [Video to Short]"
            writer.writerow(new_row)


# To-DO: Add threshold for videos above 30s which may be to short aswell.
