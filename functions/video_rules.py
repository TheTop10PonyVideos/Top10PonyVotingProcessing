"""Rule checks for videos. These functions check videos for validity and
annotate any that fail the tests. Note that this is different from annotating a
_vote_ for a video, which happens in `functions/ballot_rules.py`. Some of the
vote checks rely on videos having been checked and annotated first."""

from datetime import datetime
from classes.voting import Video


def check_uploader_blacklist(videos: list[Video], blacklisted_uploaders: list[str]):
    """Check the given list of videos against a list of blacklisted uploaders.
    Annotate any videos with a blacklisted uploader.
    """
    for video in videos:
        if video.data["uploader"] in blacklisted_uploaders:
            video.annotations.add("BLACKLISTED")


def check_uploader_whitelist(videos: list[Video], whitelisted_uploaders: list[str]):
    """Check the given list of videos against a list of whitelisted uploaders.
    Annotate any videos whose uploader is NOT on the whitelist. (This makes it
    easier to spot new or unknown creators during a manual review).
    """
    for video in videos:
        if video.data["uploader"] not in whitelisted_uploaders:
            video.annotations.add("NOT WHITELISTED")


def check_upload_date(videos: list[Video], month_date: datetime):
    """Check the given list of videos to make sure they were released in the
    given month. Annotate any videos that were released too early or too late.
    """

    lower_bound = month_date.replace(day=1)

    upper_bound = None
    if month_date.month < 12:
        upper_bound = lower_bound.replace(month=lower_bound.month + 1, day=1)
    else:
        upper_bound = lower_bound.replace(year=lower_bound.year + 1, month=1, day=1)

    for video in videos:
        upload_date = video.data["upload_date"]
        if upload_date < lower_bound:
            video.annotations.add("VIDEO TOO OLD")
        elif upload_date >= upper_bound:
            video.annotations.add("VIDEO TOO NEW")


def check_duration(videos: list[Video]):
    """Check the video durations of given list of videos. Annotate any videos
    that are (or may be) too short.
    """
    for video in videos:
        duration = video.data["duration"]
        if duration <= 30:
            video.annotations.add("VIDEO TOO SHORT")
        elif duration <= 45:
            video.annotations.add("VIDEO MAYBE TOO SHORT")
