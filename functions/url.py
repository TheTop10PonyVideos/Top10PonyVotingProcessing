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
    of query parameters, return a "normalized" URL with the minimal
    set of parameters needed, as well as the video id."""

    # Use urllib to break the URL into its relevant components.
    url_components = urlparse(url)
    path = url_components.path

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
    # Shorts URL                https://www.youtube.com/shorts/{VIDEO ID}

    video_id = None
    
    if path.split("/")[1] in ["watch", "shorts", "live"]:
        if normal_match := re.match(r"^/watch/?\?(?:.*&)?v=([a-zA-Z0-9_-]+)", f"{path}?{url_components.query}"):
            # Regular YouTube URL: eg. https://www.youtube.com/watch?v=9RT4lfvVFhA
            video_id = normal_match.group(1)
        elif shorts_match := re.match("^/shorts/([a-zA-Z0-9_-]+)", path):
            # Shorts URL: eg. https://www.youtube.com/shorts/5uFeg2BOPNo
            video_id = shorts_match.group(1)
        elif livestream_match := re.match("^/live/([a-zA-Z0-9_-]+)", path):
            # Livestream URL: eg. https://www.youtube.com/live/Q8k4UTf8jiI
            video_id = livestream_match.group(1)
    elif shortened_match := re.match("^/([a-zA-Z0-9_-]+)", path):
        # Shortened YouTube URL: eg. https://youtu.be/9RT4lfvVFhA
        video_id = shortened_match.group(1)

    if video_id is None:
        raise ValueError(f"Cannot normalize YouTube URL {url} - malformed link")
    if len(video_id) != 11:
        raise ValueError(f"Cannot normalize YouTube URL {url} - video id is not 11 characters")

    # Using the video id, construct a normalized version of the YouTube URL.
    normalized_url = f"https://www.youtube.com/watch?v={video_id}"

    return normalized_url, video_id


def normalize_derpibooru_url(url: str):
    """Given a Derpibooru URL which may contain various extraneous search query
    parameters, return a "normalized" URL with just the Derpibooru id."""
    url_components = urlparse(url)
    print(url_components)
    scheme = url_components.scheme
    netloc = url_components.netloc
    path = url_components.path

    if not path.startswith("/images/"):
        raise ValueError(f'Cannot normalize Derpibooru URL {url} - path must begin with "/images/"')

    return f"{scheme}://{netloc}{path}"
