from typing import TypedDict
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
