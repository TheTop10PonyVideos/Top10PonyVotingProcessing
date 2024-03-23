"""Rule checks for videos."""

from datetime import datetime
from classes.voting import Video


def check_blacklist(videos: list[Video], blacklisted_uploaders: list[str]):
    """Check the given list of videos against a list of blacklisted uploaders.
    Annotate any videos with a blacklisted uploader.
    """
    for video in videos:
        if video.data['uploader'] in blacklisted_uploaders:
            video.annotations.add('BLACKLISTED')

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
        upload_date = video.data['upload_date']
        if upload_date < lower_bound:
            video.annotations.add('VIDEO TOO OLD')
        elif upload_date >= upper_bound:
            video.annotations.add('VIDEO TOO NEW')

def check_duration(videos: list[Video]):
    """Check the video durations of given list of videos. Annotate any videos
    that are (or may be) too short.
    """
    for video in videos:
        duration = video.data['duration']
        if duration <= 30:
            video.annotations.add('VIDEO TOO SHORT')
        elif duration <= 45:
            video.annotations.add('VIDEO MAYBE TOO SHORT')
