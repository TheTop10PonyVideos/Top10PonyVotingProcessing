import csv
from modules import data_pulling

input_file_data_link = "modules/csv/data_link.csv"
input_file_processed_duplicates = "outputs/processed_duplicates.csv"
output_file = "outputs/processed_blacklist.csv"


def check_blacklist(input):
    with open(input, "r", encoding="utf-8") as csv_data_link, open(
        input_file_processed_duplicates, "r", encoding="utf-8"
    ) as csv_duplicates, open(
        output_file, "w", newline="", encoding="utf-8"
    ) as csv_out:
        reader_data_link = csv.reader(csv_data_link)
        reader_duplicates = csv.reader(csv_duplicates)
        writer = csv.writer(csv_out)

        for row_data_link, row_duplicates in zip(reader_data_link, reader_duplicates):
            new_row = row_data_link

            for index, cell in enumerate(row_data_link):
                if "youtube.com" in cell or "youtu.be" in cell:
                    video_id = data_pulling.extract_video_id(cell)

                    if video_id:
                        title, uploader, seconds, upload_date_str = data_pulling.yt_api(
                            video_id
                        )
                        if data_pulling.check_blacklisted_channels(uploader):
                            row_duplicates[index] += " [BLACKLISTED]"

                elif data_pulling.contains_accepted_domain(cell):
                    video_link = cell

                    if video_link:
                        print(video_link)
                        (
                            title,
                            uploader,
                            seconds,
                            upload_date_str,
                        ) = data_pulling.check_with_yt_dlp(video_link=video_link)
                        if data_pulling.check_blacklisted_channels(uploader):
                            row_duplicates[index] += " [BLACKLISTED]"

            writer.writerow(row_duplicates)
