"""Video data fetching services. To add a new service (eg. to fetch from a
different site), create a class that implements the `can_fetch`, `request`,
and `parse` methods."""

import re
from datetime import datetime
from datetime import timezone
from googleapiclient.discovery import build
from yt_dlp import YoutubeDL
from functions.date import convert_iso8601_duration_to_seconds
from functions.messages import err
from classes.exceptions import FetchRequestError, FetchParseError, VideoUnavailableError


class YouTubeFetchService:
    """Fetch service for YouTube video data. Requires a YouTube Data API key."""

    def __init__(self, api_key: str, do_build_service: bool = True):
        # Create the YouTube Data API service.
        if do_build_service:
            self.yt_service = build("youtube", "v3", developerKey=api_key)

    def extract_video_id(self, url: str) -> str:
        """Given a YouTube video URL, extract the video id from it."""

        video_id_regex = r"(?:\?v=|/embed/|/watch\?v=|/youtu.be/|live/)([a-zA-Z0-9_-]+)"

        video_id_match = re.search(video_id_regex, url)

        if video_id_match:
            return video_id_match.group(1)

        return None

    def can_fetch(self, url: str) -> bool:
        return "youtube.com" in url or "youtu.be" in url

    def request(self, url: str):
        """Query the YouTube Data API for the given URL."""
        video_id = self.extract_video_id(url)
        if video_id is None:
            raise ValueError(
                f'Could not request URL "{url}" via the YouTube Data API; unable to determine video id from URL'
            )

        # TODO: Can we use url here instead of id?
        request = self.yt_service.videos().list(
            part="status,snippet,contentDetails", id=video_id
        )

        response = None

        try:
            response = request.execute()
        except Exception as e:
            raise FetchRequestError(
                f'Could not request URL "{url}" via the YouTube Data API; error while executing request: {e}'
            ) from e

        if response is None:
            raise FetchRequestError(
                f'Could not request URL "{url}" via the YouTube Data API; no API response'
            )

        return response

    def parse(self, response) -> dict:
        """Parse video data from a YouTube Data API response."""
        if not response["items"]:
            raise VideoUnavailableError(
                f"Unable to parse response from YouTube Data API; response does not contain any items"
            )

        response_item = response["items"][0]
        snippet = response_item["snippet"]
        iso8601_duration = response_item["contentDetails"]["duration"]

        return {
            "title": snippet["title"],
            "uploader": snippet["channelTitle"],
            "upload_date": datetime.fromisoformat(snippet["publishedAt"]),
            "duration": convert_iso8601_duration_to_seconds(iso8601_duration),
        }


class YtDlpFetchService:
    """Fetch service which makes requests for video data via yt-dlp."""

    def __init__(self, accepted_domains: list[str], prompt_for_missing_durs):
        self.accepted_domains = accepted_domains
        self.prompt_dur = prompt_for_missing_durs

    def can_fetch(self, url: str) -> bool:
        """Return True if the URL contains an accepted domain (other than
        YouTube)."""

        return any(domain in url for domain in self.accepted_domains)

    def request(self, url: str):
        """Query yt-dlp for the given URL."""

        response = None

        try:
            ydl_opts = {
                "quiet": True,
            }

            with YoutubeDL(ydl_opts) as ydl:
                response = ydl.extract_info(url, download=False)

                if "entries" in response:
                    response = response["entries"][0]

        except Exception as e:
            raise FetchRequestError(
                f'Could not fetch URL "{url}" via yt-dlp; error while extracting video info: {e}'
            ) from e

        return response

    def parse(self, response) -> dict:
        # yt-dlp doesn't provide any timezone information with its timestamps,
        # but according to its source code, it looks like it uses UTC:
        # <https://github.com/yt-dlp/yt-dlp/blob/07f5b2f7570fd9ac85aed17f4c0118f6eac77beb/yt_dlp/YoutubeDL.py#L2631>
        date_format = "%Y%m%d"
        upload_date = datetime.strptime(response.get("upload_date"), date_format)
        upload_date = upload_date.replace(tzinfo=timezone.utc)

        if response.get("duration") is None and self.prompt_dur:
            mins = None
            seconds = None
            err("Missing Duration, Please Add Manually:")

            while(True):
                try:
                    if mins is None:
                        mins = int(input("Minutes: "))
                    seconds = int(input("Seconds: "))
                    break
                except: continue

            response["duration"] = mins * 60 + seconds

        if not response.get("idealized"):
            # some sites will return a display name rather than unique 
            # usernames or they might return extra things in their
            # response properties, so this is here to make adjustments
            # for an ideal response, which will skip this step if loaded from the cache
            match response["webpage_url_domain"]:
                case "twitter.com":
                    response["channel"] = response.get("uploader_id")
                    response["title"] = response.get("title")[response.get("title").find("-") + 2 :]
                case "tiktok.com":
                    response["channel"] = response.get("uploader")
                    # could be attached to the if condition, but would feel
                    # unorganizd if future sites are added that might need to use this

            # bilibili.com and newgrounds.com sites don't seem to return information for the `channel`
            # response property, so use `uploader` instead.
            if response.get("channel") is None:
                response["channel"] = response.get("uploader")

            response["idealized"] = True

        video_data = {
            "title": response.get("title"),
            "uploader": response.get("channel"),
            "upload_date": upload_date,
            "duration": response.get("duration"),
        }

        return video_data
