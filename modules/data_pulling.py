import csv, re, os
from datetime import datetime
from googleapiclient.discovery import build
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
from classes.caching import FileCache

# TODO: Use pathlib for path abstraction
# TODO: Don't use global variables

# Load environment configuration from a `.env` file if present.
load_dotenv()

API_KEY = os.getenv("apikey")  # may replace this

# Caching
response_cache_type = os.getenv("response_cache_type")
response_cache_file = os.getenv("response_cache_file")

response_cache = None
if response_cache_type == "memory":
    response_cache = {}
elif response_cache_type == "file":
    if response_cache_file is None:
        raise Exception(
            f'response_cache_type environment variable was set to "{response_cache_type}", but no response_cache_file was specified'
        )
    response_cache = FileCache(response_cache_file)

# Create the YouTube Data API service.
yt_service = build("youtube", "v3", developerKey=API_KEY)

# Global variables for tracking progress.
links_count = 0  # Used for percentage calculation
links_processed_count = 0  # Used for percentage calculation
retry_count = 0
max_retry_count = 5
current_try = 0


def yt_api(video_id: str) -> tuple:
    """Return a tuple of metadata for the given YouTube video id. The metadata
    is fetched via the YouTube Data API.
    TODO: Return a dictionary or data type with named keys
    """
    global links_processed_count
    global max_retry_count

    request = yt_service.videos().list(
        part="status,snippet,contentDetails", id=video_id
    )

    video_data = None

    # If using the response cache, check for a cached response first and use
    # that if available.
    if response_cache is not None and request.uri in response_cache:
        print("USED CACHE")
        video_data = response_cache[request.uri]
    else:
        try:
            print("USED API")
            video_data = request.execute()
        except Exception as e:
            print(f"An error occurred while querying the YouTube Data API: {e}")
            print("Retrying...")
            current_try += 1
            return

        # Cache the response if using the response cache.
        if response_cache is not None:
            response_cache[request.uri] = video_data

    try:
        if video_data is not None:
            if video_data["items"]:
                title = video_data["items"][0]["snippet"]["title"]
                uploader = video_data["items"][0]["snippet"]["channelTitle"]
                duration = video_data["items"][0]["contentDetails"]["duration"]
                upload_date = video_data["items"][0]["snippet"]["publishedAt"]
                duration_string = str(duration)
                upload_date = video_data["items"][0]["snippet"]["publishedAt"]

                seconds = iso8601_converter(duration_str=duration_string)
                links_processed_count += 1
                # percentage_processed = (links_processed_count / links_count) * 100
                # formatted_percentage = "{:.2f}%".format(percentage_processed)
                # print(f"{formatted_percentage} done ({links_count}/{links_processed_count})")
                max_retry_count = 5

                return title, uploader, seconds, upload_date
            else:
                print("[DATAPULLING] ERROR: VIDEO UNAVAILABLE")
                print(video_data)
                title = None
                uploader = None
                seconds = 0
                upload_date = None
                return title, uploader, seconds, upload_date

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Retrying...")
        print(video_data)
        current_try += 1
        return
        if current_try == max_retry_count:
            return
        # return yt_api(video_id=video_id)


# Converts ISO times into seconds (just don't touch it, if it works lol)
def iso8601_converter(duration_str: str) -> int:
    """Given an ISO 8601 duration string, return the length of that duration in
    seconds.

    Note: Apparently the isodate package can perform this conversion if needed.
    """
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


def check_with_yt_dlp(video_link: str) -> tuple:
    """Return metadata for the given video link. The metadata is fetched using
    yt-dlp.
    TODO: Remove recursive retry
    """
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
            upload_date = info.get("upload_date")
            # links_processed_count += 1
            # percentage_processed = (links_processed_count / links_count) * 100
            # formatted_percentage = "{:.2f}%".format(percentage_processed)
            # print(
            # f"{formatted_percentage} done ({links_count}/{links_processed_count})"
            # )
            return title, uploader, duration, upload_date

    except Exception as e:
        print(f"An error occurred: {e}")
        # print("Retrying...")
        # retry_count += 1
        # if retry_count > max_retry_count:
        #    return
        # return check_with_yt_dlp(video_link)


def extract_video_id(url: str) -> str:
    """Given a YouTube video URL, extract the video id from it."""

    video_id_regex = r"(?:\?v=|/embed/|/watch\?v=|/youtu.be/)([a-zA-Z0-9_-]+)"

    video_id_match = re.search(video_id_regex, url)

    if video_id_match:
        return video_id_match.group(1)

    return None


def check_blacklisted_channels(channel: str) -> bool:
    """Return true if the blacklist file contains the given channel. The list of
    blacklisted channels is in `modules/csv/blacklist.csv`"""
    with open(checker_file, "r", encoding="utf-8") as check:
        checker = csv.reader(check)

        for row in checker:
            for cell in row:
                try:
                    if channel in cell:
                        return True
                except Exception as e:
                    print(f"ERROR: {e}")
                    return False
    return False


def contains_accepted_domain(cell: str) -> bool:
    """Return True if cell contains the name of an accepted domain. The list of
    accepted domains is in `modules/csv/accepted_domains.csv`.
    """

    return any(domain in cell for domain in accepted_domains)


# why is this here :P hmmmmmmmmmmmmmmm anyways don't touch it :D
checker_file = "modules/csv/blacklist.csv"

with open("modules/csv/accepted_domains.csv", "r") as csvfile:
    reader = csv.reader(csvfile)
    accepted_domains = [
        row[0] for row in reader
    ]  # Initialize list of accepted domains for checks later
