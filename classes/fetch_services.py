"""Video data fetching services. To add a new service (eg. to fetch from a
different site), create a class that implements the `can_fetch`, `request`,
and `parse` methods."""

import re, pytz, hashlib, requests
from datetime import datetime
from urllib.parse import urlparse
from googleapiclient.discovery import build
from yt_dlp import YoutubeDL
from functions.date import convert_iso8601_duration_to_seconds
from functions.url import normalize_youtube_url
from functions.messages import err
from data.globals import ydl_opts
from classes.exceptions import FetchRequestError, FetchParseError, VideoUnavailableError
from classes.typing import VideoData
from functions.messages import inf


class YouTubeFetchService:
    """Fetch service for YouTube video data. Requires a YouTube Data API key when fetching video data."""

    def __init__(self, api_key: str = None):
        # Create the YouTube Data API service.
        if api_key:
            self.yt_service = build("youtube", "v3", developerKey=api_key)

    def extract_video_id(self, url: str) -> str:
        """Given a YouTube video URL, extract the video id from it, or None if
        no video id can be extracted."""

        try:
            _, video_id = normalize_youtube_url(url)
        except:
            return None

        return video_id

    def can_fetch(self, url: str) -> bool:
        return "youtube.com" in url or "youtu.be" in url

    def request(self, url: str) -> VideoData:
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
            "platform": "YouTube",
        }

    def parse(self, video_data) -> VideoData:
        """Parse video data from a YouTube Data API response."""

        upload_date = datetime.fromisoformat(video_data.get("upload_date"))

        return {
            "title": video_data.get("title"),
            "uploader": video_data.get("uploader"),
            "upload_date": upload_date,
            "duration": video_data.get("duration"),
            "platform": "YouTube",
        }


class DerpibooruFetchService:
    """Fetch service for Derpibooru video data."""

    def can_fetch(self, url: str) -> bool:
        return "derpibooru.org" in url

    def request(self, url: str) -> VideoData:
        """Query the Derpibooru API for the given URL."""
        id_match = re.search("derpibooru.org/images/([0-9]+)", url)

        if not id_match:
            raise ValueError(
                f'Could not request URL "{url}" via the Derpibooru Data API; unable to determine video id from URL'
            )
        
        post_id = id_match.group(1)
        response = None

        try:
            response = requests.get(f"https://derpibooru.org/api/v1/json/images/{post_id}")
        except requests.exceptions.ContentDecodingError as e:
            raise FetchRequestError(
                f'Could not request URL "{url}" via the Derpibooru API; invalid post id'
            ) from e
        except Exception as e:
            raise FetchRequestError(
                f'Could not request URL "{url}" via the Derpibooru API'
            ) from e
        
        if response.status_code != 200:
            raise FetchRequestError(
                f'Could not request URL "{url}" via the Derpibooru API; received status code {response.status_code}'
            )

        response = response.json()["image"]

        return {
            "title": f"Derpibooru post #{post_id}",
            "uploader": response.get("uploader"),
            "upload_date": response.get("created_at"),
            "duration": response.get("duration"),
            "platform": "Derpibooru",
        }

    def parse(self, video_data) -> VideoData:
        """Parse video data from a Derpibooru API response."""

        upload_date = datetime.fromisoformat(video_data.get("upload_date"))

        return {
            "title": video_data.get("title"),
            "uploader": video_data.get("uploader"),
            "upload_date": upload_date,
            "duration": video_data.get("duration"),
            "platform": "Derpibooru",
        }


class YtDlpFetchService:
    """Fetch service which makes requests for video data via yt-dlp."""

    def __init__(self, accepted_domains: list[str]):
        self.accepted_domains = accepted_domains
        if "cookiefile" not in ydl_opts:
            inf("Note: Couldn't find data/cookies.txt file. Some requests may yield no data.")

    def can_fetch(self, url: str) -> bool:
        """Return True if the URL contains an accepted domain (other than
        YouTube)."""

        return any(domain in url for domain in self.accepted_domains)

    def request(self, url: str) -> VideoData:
        """Query yt-dlp for the given URL."""

        url_components = urlparse(url)
        site = url_components.netloc.split(".")
        site = site[0] if len(site) == 2 else site[1]

        try:
            with YoutubeDL(ydl_opts) as ydl:
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
                site = "twitter"
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
                site = "bluesky"
                uploader = response.get("uploader_id")
                response["channel"] = uploader[:uploader.index(".")] if uploader else None
                response["title"] = (
                    f"Bluesky post by {response['channel']} ({self.hash_str(response['title'])})"
                )
                err("Response from Bluesky does not contain video duration")
            case "pony":
                site = "PonyTube"
            case "thishorsie":
                site = "ThisHorsieRocks"
            case "instagram":
                # Default response["title"] is too normalized so use thumbnail for hash
                response["title"] = (
                    f"Instagram video by {response['channel']} ({self.hash_str(response['thumbnail'])})"
                )

        return {
            "title": response.get("title"),
            "uploader": response.get("channel"),
            "upload_date": response.get("upload_date"),
            "duration": response.get("duration"),
            "platform": site.capitalize(),
        }

    def parse(self, video_data) -> VideoData:
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
            "platform": video_data.get("platform"),
        }

    # Some sites like X and Tiktok don't have a designated place to put a title for
    # posts so the 'titles' are hashed here to reduce the chance of similarity detection
    # between different posts by the same uploader. Larger hash substrings decrease this chance
    def hash_str(self, string):
        h = hashlib.sha256()
        h.update(string.encode())
        return h.hexdigest()[:5]


class B23FetchService:
    """Fetch service for b23.tv links."""

    def __init__(self, ytdlp_fetch_service: YtDlpFetchService):
        self.ytdlp_fetch_service = ytdlp_fetch_service

    def can_fetch(self, url: str) -> bool:
        return "b23.tv" in url

    def request(self, url: str) -> VideoData:
        """Perform an intermediary step of getting the true video url
        from the b23.tv redirect before requesting using yt-dlp."""

        id_match = re.search("b23.tv/([0-9a-zA-Z]+)", url)

        if not id_match:
            raise ValueError(
                f'Could not request URL "{url}"; unable to determine video id from URL'
            )

        share_id = id_match.group(1)

        response = requests.get(f"https://b23.tv/{share_id}", allow_redirects=False)

        if response.status_code != 302:
            raise VideoUnavailableError(f"No video link was returned by {url}")

        video_url = re.sub(r"\?.+", "", response.next.url) # remove unnecessary tracking params

        return self.ytdlp_fetch_service.request(video_url)

    def parse(self, video_data) -> VideoData:
        """Parse video data using the yt-dlp fetch service."""
        return self.ytdlp_fetch_service.parse(video_data)
