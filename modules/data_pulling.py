import csv
import re
from datetime import datetime
from googleapiclient.discovery import build
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("apikey")  # may replace this

youtube = build("youtube", "v3", developerKey=API_KEY)
links_count = 0  # Used for percentage calculation
links_processed_count = 0  # Used for percentage calculation
max_retry_count = 5


def set_count(input):
    global links_count
    with open(input, "r") as file:
        csv_reader = csv.reader(file)

        for row in csv_reader:
            for cell in row:
                if "http" in cell:
                    links_count += 4  # this will be updated to "1" after we only need one datapulling fetch soon TM


# This is the API fetch through youtube. Usage: title, uploader, duration = data_pulling.yt_api(video_id)
def yt_api(video_id):
    global links_processed_count
    global max_retry_count
    try:
        video_data = (
            youtube.videos()
            .list(part="status,snippet, contentDetails", id=video_id)
            .execute()
        )

        title = video_data["items"][0]["snippet"]["title"]
        uploader = video_data["items"][0]["snippet"]["channelTitle"]
        duration = video_data["items"][0]["contentDetails"]["duration"]
        upload_date = video_data["items"][0]["snippet"]["publishedAt"]
        durationString = str(duration)
        upload_date = video_data["items"][0]["snippet"]["publishedAt"]

        seconds = iso8601_converter(duration_str=durationString)
        links_processed_count += 1
        percentage_processed = (links_processed_count / links_count) * 100
        formatted_percentage = "{:.2f}%".format(percentage_processed)
        print(f"{formatted_percentage} done ({links_count}/{links_processed_count})")
        max_retry_count = 0
        return title, uploader, seconds, upload_date

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Retrying...")

        return yt_api(video_id=video_id)


# Converts ISO times into seconds (just don't touch it, if it works lol)
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


# The yt_dlp check. Same usage as yt_api.
def check_with_yt_dlp(video_link):
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
            upload_date = info.get("upload_date")
            durationString = str(duration)
            seconds = iso8601_converter(duration_str=durationString)
            upload_date = info.get("upload_date")
            links_processed_count += 1
            percentage_processed = (links_processed_count / links_count) * 100
            formatted_percentage = "{:.2f}%".format(percentage_processed)
            print(
                f"{formatted_percentage} done ({links_count}/{links_processed_count})"
            )
            return title, uploader, seconds, upload_date

    except Exception as e:
        max_retry_count
        print(f"An error occurred: {e}")
        print("Retrying...")
        retry_count += 1
        if max_retry_count == retry_count:
            return
        return check_with_yt_dlp(video_link)


# YT API needs the video id not the link! Call this regex function to extract the video id (video_id = data_pulling.extract_video_id(cell))
def extract_video_id(url):
    video_id_match = re.search(
        r"(?:\?v=|/embed/|/watch\?v=|/youtu.be/)([a-zA-Z0-9_-]+)", url
    )
    if video_id_match:
        return video_id_match.group(1)
    return None


# why is this here :P hmmmmmmmmmmmmmmm anyways don't touch it :D
checker_file = "modules/csv/blacklist.csv"


def check_blacklisted_channels(channel):
    with open(checker_file, "r", encoding="utf-8") as check:
        checker = csv.reader(check)

        for row in checker:
            for cell in row:
                if channel in cell:
                    return True
    return False


with open("modules/csv/accepted_domains.csv", "r") as csvfile:
    reader = csv.reader(csvfile)
    accepted_domains = [
        row[0] for row in reader
    ]  # Initialize list of accepted domains for checks later


def contains_accepted_domain(cell):
    # Returns true if cell contains the name of an accepted domain
    # The list of accepted domains are in modules/csv/accepted_domains.csv
    return any(domain in cell for domain in accepted_domains)
