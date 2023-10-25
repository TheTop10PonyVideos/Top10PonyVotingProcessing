import csv
import re
from googleapiclient.discovery import build
from yt_dlp import YoutubeDL


API_KEY = "E"  # may replace this

youtube = build("youtube", "v3", developerKey=API_KEY)
links_count = 0
links_processed_count = 0

with open("modules/csv/datalinks.csv", "r") as file:
    csv_reader = csv.reader(file)

    for row in csv_reader:
        for cell in row:
            if "http" in cell:
                links_count += 2  # this will be updated to "1" after we only need one datapulling fetch soon TM


def check_privacy_and_get_title(video_id):
    global links_processed_count
    try:
        video_data = (
            youtube.videos()
            .list(part="status,snippet, contentDetails", id=video_id)
            .execute()
        )

        status = video_data["items"][0]["status"]["privacyStatus"]
        title = video_data["items"][0]["snippet"]["title"]
        uploader = video_data["items"][0]["snippet"]["channelTitle"]
        duration = video_data["items"][0]["contentDetails"]["duration"]
        durationString = str(duration)
        # print(durationString)

        seconds = iso8601_converter(duration_str=durationString)
        # print(seconds)
        # print(f'Fetched state for {title}. Status: {status}, Uploader: {uploader}')
        links_processed_count += 1
        percentage_processed = (links_processed_count / links_count) * 100
        formatted_percentage = "{:.2f}%".format(percentage_processed)
        print(f"{formatted_percentage} done ({links_count}/{links_processed_count})")
        return title, status, uploader, seconds

    except Exception as e:
        return None, f"Error: {str(e)}"


def iso8601_converter(duration_str):
    if duration_str.startswith("PT"):
        duration_str = duration_str[2:]

    total_seconds = 0
    hours = 0
    minutes = 0
    seconds = 0

    if "H" in duration_str:
        hours_part, duration_str = duration_str.split("H")
        hours = int(hours_part)

    if "M" in duration_str:
        minutes_part, duration_str = duration_str.split("M")
        minutes = int(minutes_part)

    if "S" in duration_str:
        seconds_part = duration_str.replace("S", "")
        seconds = int(seconds_part)

    total_seconds = hours * 3600 + minutes * 60 + seconds

    return total_seconds


def check_withYtDlp(video_link):
    global links_processed_count
    try:
        ydl_opts = {
            "quiet": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_link, download=False)

            if "entries" in info:
                info = info["entries"][0]

            title = info.get("title")
            uploader = info.get("uploader")
            duration = info.get("duration")
            durationString = str(duration)
            # print(durationString)
            seconds = iso8601_converter(duration_str=durationString)

            # print(f'Fetched state for {title}. Uploader: {uploader}')
            # print(f'Duration: {duration} seconds')
            links_processed_count += 1
            percentage_processed = (links_processed_count / links_count) * 100
            formatted_percentage = "{:.2f}%".format(percentage_processed)
            print(
                f"{formatted_percentage}% done ({links_count}/{links_processed_count})"
            )
            return title, uploader, seconds

    except Exception as e:
        print(f"An error occurred: {e}")
        return None, f"Error: {str(e)}"


def extract_video_id(url):
    video_id_match = re.search(
        r"(?:\?v=|/embed/|/watch\?v=|/youtu.be/)([a-zA-Z0-9_-]+)", url
    )
    if video_id_match:
        return video_id_match.group(1)
    return None


checker_file = "modules/csv/blacklist.csv"


def checkBlacklistedChannels(channel):
    with open(checker_file, "r", encoding="utf-8") as check:
        checker = csv.reader(check)

        for row in checker:
            for cell in row:
                if channel in cell:
                    return True
    return False
