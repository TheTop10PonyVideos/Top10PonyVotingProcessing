import csv
from datetime import datetime
from pytz import timezone
from modules import data_pulling

input_file_data_link = "modules/csv/data_link.csv"
input_file_blacklist = "outputs/processed_blacklist.csv"
output_file = "outputs/processedDates.csv"

today = datetime.today()
zone = timezone("Etc/GMT-14")
today = datetime.now(zone)
limit_date = datetime(today.year, today.month - 1, 1)


def parse_youtube_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")


def parse_yt_dlp_date(date_str):
    return datetime.strptime(date_str, "%Y%m%d")


def check_dates(input):
    with open(input, "r", encoding="utf-8") as csv_data_link, open(
        input_file_blacklist, "r", encoding="utf-8"
    ) as csv_blacklist, open(output_file, "w", newline="", encoding="utf-8") as csv_out:
        reader_data_link = csv.reader(csv_data_link)
        reader_blacklist = csv.reader(csv_blacklist)
        writer = csv.writer(csv_out)

        for row_data_link, row_blacklist in zip(reader_data_link, reader_blacklist):
            new_row = row_data_link

            for index, cell in enumerate(row_data_link):
                if "youtube.com" in cell or "youtu.be" in cell:
                    video_id = data_pulling.extract_video_id(cell)

                    if video_id:
                        title, uploader, seconds, upload_date_str = data_pulling.yt_api(
                            video_id
                        )
                        upload_date = parse_youtube_date(upload_date_str)
                        if upload_date <= limit_date:
                            row_blacklist[index] += " [Video too old]"

                elif (
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
                            seconds,
                            upload_date_str,
                        ) = data_pulling.check_with_yt_dlp(video_link=video_link)
                        upload_date = parse_yt_dlp_date(upload_date_str)
                        if upload_date <= limit_date:
                            row_blacklist[index] += " [Video too old]"

            writer.writerow(row_blacklist)
