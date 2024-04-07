# TODO: Deprecate `GetVideoMetadataError` class when modules are removed
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


class SchemaValidationError(Exception):
    """Raised when data doesn't match the expected schema; eg. a video that has
    no title attribute. This usually indicates that a fetch service needs to be
    updated to provide the expected data."""

    pass


class VideoUnavailableError(Exception):
    """Raised when a video URL is correct, but the video itself is
    being withheld by its service for whatever reason.
    """

    pass
