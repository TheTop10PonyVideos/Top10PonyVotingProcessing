from typing import TypedDict, NotRequired
from collections.abc import Callable


class ArchiveRecord(TypedDict):
    year: str
    month: str
    rank: str
    link: str
    title: str
    channel: str
    upload_date: str
    state: str
    alternate_link: str
    found: str
    notes: str


class VideoData(TypedDict):
    title: str
    uploader: str
    upload_date: str
    duration: str
    platform: str


class StatusRow(TypedDict):
    row: int
    url: str
    title: str
    new_title: NotRequired[str]
    prev_status: NotRequired[str]
    new_status: str
    note: NotRequired[str]
    blocked_countries: NotRequired[str]
