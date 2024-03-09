from dataclasses import dataclass
from datetime import datetime

@dataclass
class VideoMetadata:
    """Video metadata dataclass."""
    title: str
    uploader: str
    duration : int
    upload_date: datetime
    source: str
