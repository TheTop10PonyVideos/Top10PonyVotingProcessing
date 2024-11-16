from functions.services import get_fetcher
from functions.messages import suc, inf, err


def fetch_videos_data(yt_api_key: str, urls: list[str]) -> dict[str, dict]:
    """Given a list of video URLs, return a dictionary mapping each URL to its
    data."""
    fetcher = get_fetcher(yt_api_key)

    videos_data = {}
    for url in urls:
        video_data = None
        try:
            video_data = fetcher.fetch(url)
        except Exception as e:
            err(f"WARNING: Could not fetch data for URL {url}")

        videos_data[url] = video_data

    return videos_data
