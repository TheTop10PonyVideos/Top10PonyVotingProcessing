# TODO: Deprecate when modules are removed
class GetVideoMetadataError(Exception):
    pass


class UnsupportedHostError(Exception):
    """Raised when an attempt is made to fetch a URL that is not supported by
    the application.
    """

    pass


class FetchRequestError(Exception):
    """Raised when an API request is made, but fails for some reason (eg.
    incorrect credentials, connection error, etc.)
    """

    pass


class FetchParseError(Exception):
    """Raised when an API request succeeds, but the resulting response can't be
    parsed into video data."""

    pass


class VideoUnavailableError(Exception):
    """Raised when a video URL is correct, but the video itself is
    being withheld by its service for whatever reason.
    """

    pass
