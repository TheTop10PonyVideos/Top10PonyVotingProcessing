"""Rule checks for videos. These functions check videos for validity and
annotate any that fail the tests. Note that this is different from annotating a
_vote_ for a video, which happens in `functions/ballot_rules.py`. Some of the
vote checks rely on videos having been checked and annotated first."""

from datetime import datetime
from pytz import timezone
from functions.date import get_month_year_bounds
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


def check_upload_date(videos: list[Video], month: int, year: int):
    """Check the given list of videos to make sure they were released in the
    given month. Annotate any videos that were released too early or too late.

    For maximum leniency, the lower and upper date bounds are in the earliest
    and latest timezones respectively; this means, for example, that a video
    uploaded on 1st April could still be eligible for the March voting as long
    as it was still March _somewhere_ in the world when it was uploaded.
    """

    lower_bound, upper_bound = get_month_year_bounds(month, year, True)

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
        
        if not duration:
            video.annotations.add("MISSING DURATION")        
        elif duration <= 30:
            video.annotations.add("VIDEO TOO SHORT")
        elif duration <= 45:
            video.annotations.add("VIDEO MAYBE TOO SHORT")
