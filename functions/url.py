"""Functions for operating on video URLs."""

import re
from urllib.parse import urlparse, parse_qs


def get_youtube_domains() -> list[str]:
    """Return a list of permitted YouTube web domains."""
    return ["m.youtube.com", "www.youtube.com", "youtube.com", "youtu.be"]


def is_youtube_url(url: str) -> bool:
    """Return True if the given URL contains one of the YouTube web domains."""

    youtube_domains = get_youtube_domains()
    url_components = urlparse(url)

    return url_components.netloc in youtube_domains


def normalize_youtube_url(url: str):
    """Given a YouTube URL which may contain various combinations and orderings
    of query parameters, return a "normalized" URL which contains the minimal
    set of parameters needed."""

    # Use urllib to break the URL into its relevant components.
    url_components = urlparse(url)
    netloc = url_components.netloc
    path = url_components.path
    query_params = parse_qs(url_components.query)

    # Raise an exception if this isn't a YouTube URL.
    if not is_youtube_url(url):
        raise ValueError(f"Cannot normalize URL {url}; this is not a YouTube URL")

    # Parse the URL to retrieve the video id, which is the only parameter we
    # care about for the purpose of normalization. We currently recognize the
    # following types of YouTube URL, some of which have the video id in a
    # different place:
    #
    # Regular YouTube URL:      https://www.youtube.com/watch?v={VIDEO ID}
    # No-subdomain YouTube URL: https://youtube.com/watch?v={VIDEO ID}
    # Mobile YouTube URL:       https://m.youtube.com/watch?v={VIDEO ID}
    # Livestream URL:           https://www.youtube.com/live/{VIDEO ID}
    # Shortened URL:            https://youtu.be/{VIDEO ID}

    video_id = None

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

    # Using the video id, construct a normalized version of the YouTube URL.
    normalized_url = f"https://www.youtube.com/watch?v={video_id}"

    return normalized_url
