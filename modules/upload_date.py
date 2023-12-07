import csv
from datetime import datetime
from pytz import timezone
from modules import data_pulling

input_file_data_link = "modules/csv/data_link.csv"
input_file_blacklist = "outputs/processed_blacklist.csv"
output_file = "outputs/processed_dates.csv"

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
            updated_blacklist_row = list(row_blacklist)  # Preserve original content

            for index, cell in enumerate(row_blacklist):
                if index % 2 == 0:  # Process every other cell
                    if index // 2 < len(row_data_link):
                        link = row_data_link[index // 2]
                        if "youtube.com" in link or "youtu.be" in link:
                            video_id = data_pulling.extract_video_id(link)

                            if video_id:
                                title, uploader, seconds, upload_date_str = data_pulling.yt_api(video_id)
                                upload_date = parse_youtube_date(upload_date_str)
                                if upload_date <= limit_date:
                                    updated_blacklist_row[index + 1] = "Video too old"

                        elif data_pulling.contains_accepted_domain(link):
                            (
                                title,
                                uploader,
                                seconds,
                                upload_date_str,
                            ) = data_pulling.check_with_yt_dlp(video_link=link)
                            upload_date = parse_yt_dlp_date(upload_date_str)
                            if upload_date <= limit_date:
                                updated_blacklist_row[index + 1] = "Video too old"

            writer.writerow(updated_blacklist_row)
