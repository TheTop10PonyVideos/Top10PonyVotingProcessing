import csv
from datetime import datetime
from pytz import timezone
from modules import data_pulling

input_file = "WEGOTTAMAKETHEORDERCLEAR.csv"  # comment this tomorrow
output_file = "outputs/processed.csv"
today = datetime.today()
zone = timezone("Etc/GMT-14")
today = datetime.now(zone)
limit_date = datetime(today.year, today.month, 1)


def checkUploaddate():
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
                        (
                            title,
                            privacy_state,
                            uploader,
                            duration,
                            upload_date,
                        ) = data_pulling.ytAPI(video_id)

                        date = zone.localize(upload_date)

                        if date <= limit_date:
                            new_row[index] = cell + " [Video too old]"
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
                                upload_date,  # UPLOAD DATE IN RELEVANT TIMEZONE
                            ) = data_pulling.check_withYtDlp(video_link=video_link)

                            date = zone.localize(upload_date)

                            if date <= limit_date:
                                new_row[index] = cell + " [Video too old]"
            writer.writerow(new_row)
