"""Video data fetching services. To add a new service (eg. to fetch from a
different site), create a class that implements the `can_fetch`, `request`,
and `parse` methods."""

import re, pytz, hashlib, os
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build
from yt_dlp import YoutubeDL
from functions.date import convert_iso8601_duration_to_seconds
from functions.url import is_youtube_url
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

        if not is_youtube_url(url):
            return None

        video_id = None

        url_components = urlparse(url)
        path = url_components.path
        query_params = parse_qs(url_components.query)

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
                f"Response from YouTube Data API does not contain any items"
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
            "uploader": video_data.get("uploader"),
            "upload_date": upload_date,
            "duration": video_data.get("duration"),
        }


class YtDlpFetchService:
    """Fetch service which makes requests for video data via yt-dlp."""

    def __init__(self, accepted_domains: list[str]):
        self.accepted_domains = accepted_domains
        self.ydl_opts = {
            "quiet": True,
            #                                               Odysee            pony.tube & pt.thishorsie.rocks                                              ytdlp may fall back to the generic extractor if another fails
            "allowed_extractors": ["twitter", "Newgrounds", "lbry", "TikTok",           "PeerTube",         "vimeo", "BiliBili", "dailymotion", "Bluesky", "generic"]
        }

        # Previously, some twitter votes returned no data due to content being restricted
        if os.path.exists("data/cookies.txt"):
            self.ydl_opts["cookiefile"] = "data/cookies.txt"

    def can_fetch(self, url: str) -> bool:
        """Return True if the URL contains an accepted domain (other than
        YouTube)."""

        return any(domain in url for domain in self.accepted_domains)

    def request(self, url: str):
        """Query yt-dlp for the given URL."""

        url_components = urlparse(url)
        site = url_components.netloc.split(".")
        site = site[0] if len(site) == 2 else site[1]

        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                response = ydl.extract_info(url, download=False)

                if "entries" in response:
                    response = response["entries"][0]

        except Exception as e:
            raise FetchRequestError(
                f'Could not fetch URL "{url}" via yt-dlp; error while extracting video info: {e}'
            ) from e

        # Some urls might have specific issues that should
        # be handled here before they can be properly processed
        # If yt-dlp gets any updates that resolve any of these issues
        # then the respective case should be updated accordingly
        match site:
            case "twitter" | "x":
                response["channel"] = response.get("uploader_id")
                response["title"] = (
                    f"X post by {response.get('uploader_id')} ({self.hash_str(response.get('title'))})"
                )

                # This type of url means that the post has more than one video
                # and ytdlp will only successfully retrieve the duration if
                # the video is at index one
                if (
                    url[0 : url.rfind("/")].endswith("/video")
                    and int(url[url.rfind("/") + 1 :]) != 1
                ):
                    err("This X post has several videos and the fetched duration is innacurate. So it has been ignored")
                    response["duration"] = None

            case "newgrounds":
                response["channel"] = response.get("uploader")
                err("Response from Newgrounds does not contain video duration")

            case "tiktok":
                response["channel"] = response.get("uploader")
                response["title"] = (
                    f"Tiktok video by {response.get('uploader')} ({self.hash_str(response.get('title'))})"
                )

            case "bilibili":
                response["channel"] = response.get("uploader")
            
            case "bsky":
                uploader = response.get("uploader_id")
                response["channel"] = uploader[:uploader.index(".")] if uploader else None
                response["title"] = (
                    f"Bluesky post by {response['channel']} ({self.hash_str(response['title'])})"
                )
                err("Response from Bluesky does not contain video duration")

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
        upload_date = pytz.utc.localize(upload_date)

        return {
            "title": video_data.get("title"),
            "uploader": video_data.get("uploader"),
            "upload_date": upload_date,
            "duration": video_data.get("duration"),
        }

    # Some sites like X and Tiktok don't have a designated place to put a title for
    # posts so the 'titles' are hashed here to reduce the chance of similarity detection
    # between different posts by the same uploader. Larger hash substrings decrease this chance
    def hash_str(self, string):
        h = hashlib.sha256()
        h.update(string.encode())
        return h.hexdigest()[:5]
