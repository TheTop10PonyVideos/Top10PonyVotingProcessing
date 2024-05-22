"""Video data fetching services. To add a new service (eg. to fetch from a
different site), create a class that implements the `can_fetch`, `request`,
and `parse` methods."""

import re
from datetime import datetime
from datetime import timezone
from urllib.parse import urlparse, parse_qs
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
        """Given a YouTube video URL, extract the video id from it, or None if
        no video id can be extracted."""

        video_id = None

        url_components = urlparse(url)
        netloc = url_components.netloc
        path = url_components.path
        query_params = parse_qs(url_components.query)

        if netloc not in ["www.youtube.com", "youtu.be"]:
            return None

        # Regular YouTube URL: eg. https://www.youtube.com/watch?v=9RT4lfvVFhA
        if path == "/watch":
            video_id = query_params["v"][0]
        else:
            livestream_match = re.match("^/live/([a-zA-Z0-9_-]+)", path)
            shortened_match = re.match("^/([a-zA-Z0-9_-]+)", path)

            if livestream_match:
                # Livestream URL: eg. https://www.youtube.com/live/Q8k4UTf8jiI
                video_id = livestream_match.group(1)
            elif shortened_match:
                # Shortened YouTube URL: eg. https://youtu.be/9RT4lfvVFhA
                video_id = shortened_match.group(1)

        return video_id

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
            "upload_date": snippet["publishedAt"],
            "duration": convert_iso8601_duration_to_seconds(iso8601_duration),
        }

    def parse(self, video_data) -> dict:
        """Parse video data from a YouTube Data API response."""

        upload_date = datetime.fromisoformat(video_data.get("upload_date"))

        return {
            "title": video_data.get("title"),
            "uploader": video_data.get("channel"),
            "upload_date": upload_date,
            "duration": video_data.get("duration"),
        }


class YtDlpFetchService:
    """Fetch service which makes requests for video data via yt-dlp."""

    def __init__(self, accepted_domains: list[str]):
        self.accepted_domains = accepted_domains
        self.ydl_opts = {
            "quiet": True,
        }

    def can_fetch(self, url: str) -> bool:
        """Return True if the URL contains an accepted domain (other than
        YouTube)."""

        return any(domain in url for domain in self.accepted_domains)

    def request(self, url: str):
        """Query yt-dlp for the given URL."""

        response = None

        preprocess_changes = self.preprocess(url)

        if preprocess_changes and preprocess_changes.get("url"):
            url = preprocess_changes.pop("url")

        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                response = ydl.extract_info(url, download=False)

                if "entries" in response:
                    response = response["entries"][0]

        except Exception as e:
            raise FetchRequestError(
                f'Could not fetch URL "{url}" via yt-dlp; error while extracting video info: {e}'
            ) from e

        # preprocess_changes contains the response key that should be assigned a new value,
        # and corrected, which can either be a different response key that has the value we
        # originally wanted, None if the response key has an incorrect value with no substitutes,
        # or a lambda function that modifies the value assigned to the respose key
        if len(preprocess_changes):
            for response_key, corrected in preprocess_changes.items():
                if corrected is None:
                    response[response_key] = None
                elif isinstance(corrected, str):
                    response[response_key] = response.get(corrected)
                else:
                    response[response_key] = corrected(response)
            
        return {
            "title": response.get("title"),
            "uploader": response.get("channel"),
            "upload_date": response.get("upload_date"),
            "duration": response.get("duration"),
        }

    def parse(self, video_data):
        # yt-dlp doesn't provide any timezone information with its timestamps,
        # but according to its source code, it looks like it uses UTC:
        # <https://github.com/yt-dlp/yt-dlp/blob/07f5b2f7570fd9ac85aed17f4c0118f6eac77beb/yt_dlp/YoutubeDL.py#L2631>
        date_format = "%Y%m%d"
        upload_date = datetime.strptime(video_data.get("upload_date"), date_format)
        upload_date = upload_date.replace(tzinfo=timezone.utc)

        return {
            "title": video_data.get("title"),
            "uploader": video_data.get("channel"),
            "upload_date": upload_date,
            "duration": video_data.get("duration"),
        }

    # Some urls might have specific issues that should
    # be handled here before they can be properly processed
    # If yt-dlp gets any updates that resolve any of these issues
    # then the respective case should be updated accordingly
    def preprocess(self, url: str) -> dict | None:
        pattern = r'https?://(www\.)?([^/#?\.]+)'
        match = re.search(pattern, url)
        site = match.group(2)
        changes = {}

        match site:
            case "x":
                url = "https://twitter" + url[url.find("://") + 4 :]
                changes = self.preprocess(url)
                changes["url"] = url
            
            case "twitter":
                changes["channel"] = "uploader_id"
                changes["title"] = lambda video_data: f"X post by {video_data.get("uploader_id")}"
                if url[0 : url.rfind("/")].endswith("/video") and int(url[url.rfind("/") + 1:]) != 1:
                    err("This post has several videos and the fetched duration is innacurate. So it has been ignored")
                    changes["duration"] = None

            case "newgrounds":
                changes["channel"] = "uploader"
                err("Missing Duration")
            
            case "tiktok":
                changes["channel"] = "uploader"
                changes["title"] = lambda video_data: f"Tiktok video by {video_data.get("uploader")}"

            case "bilibili":
                changes["channel"] = "uploader"
                
        return changes