"""General functions for dealing with awkward dates and durations."""

import re
from datetime import datetime
from pytz import timezone


def parse_votes_csv_timestamp(timestamp: str) -> datetime:
    """Parse the timestamp from the votes CSV file into a datetime object.

    The timestamp is in the format M/D/Y h:m:s, where - annoyingly - M, D, and h
    can have either 1 or 2 digits. Python's `strptime` parser isn't able to
    handle that, so we have to preprocess the date a little first.
    """

    timestamp = timestamp.strip()
    pattern = "^(\d+)/(\d+)/(\d+) (\d+):(\d+):(\d+)$"
    match = re.match(pattern, timestamp)
    try:
        date_components = match.groups()
    except AttributeError:
        raise ValueError(
            f'Cannot parse votes CSV timestamp "{timestamp}"; invalid format'
        )

    if len(date_components) != 6:
        raise ValueError(
            f'Cannot parse votes CSV timestamp "{timestamp}"; invalid format'
        )

    month, day, year, hour, minute, second = date_components
    month = month.zfill(2)
    day = day.zfill(2)
    year = year.zfill(4)
    hour = hour.zfill(2)
    minute = minute.zfill(2)
    second = second.zfill(2)

    processed_timestamp = f"{month}/{day}/{year} {hour}:{minute}:{second}"

    timestamp_format = "%m/%d/%Y %H:%M:%S"
    dt = datetime.strptime(processed_timestamp, timestamp_format)

    return dt.replace(tzinfo=None)


def format_votes_csv_timestamp(dt: datetime) -> str:
    """Format a datetime into the timestamp format used by the votes CSV
    (M/D/Y h:m:s)
    """
    month = dt.month
    day = dt.day
    year = dt.year
    hour = dt.hour
    minute = str(dt.minute).zfill(2)
    second = str(dt.second).zfill(2)
    return f"{month}/{day}/{year} {hour}:{minute}:{second}"


def convert_iso8601_duration_to_seconds(iso8601_duration: str) -> int:
    """Given an ISO 8601 duration string, return the length of that duration in
    seconds.

    Note: Apparently the isodate package can perform this conversion if needed.
    """
    if iso8601_duration.startswith("PT"):
        iso8601_duration = iso8601_duration[2:]

    total_seconds, hours, minutes, seconds = 0, 0, 0, 0

    if "H" in iso8601_duration:
        hours_part, iso8601_duration = iso8601_duration.split("H")
        hours = int(hours_part)

    if "M" in iso8601_duration:
        minutes_part, iso8601_duration = iso8601_duration.split("M")
        minutes = int(minutes_part)

    if "S" in iso8601_duration:
        seconds_part = iso8601_duration.replace("S", "")
        seconds = int(seconds_part)

    total_seconds = hours * 3600 + minutes * 60 + seconds

    return total_seconds


def get_preceding_month_date(date: datetime) -> datetime:
    """Given a date, return the date corresponding to the first day of the
    preceding month.
    """
    preceding_month = date.month - 1 if date.month > 1 else 12
    preceding_year = date.year if date.month > 1 else date.year - 1
    return datetime(preceding_year, preceding_month, 1, tzinfo=date.tzinfo)


def get_month_bounds(date: datetime) -> tuple[datetime, datetime]:
    """Given a date, return the two dates that bound that date's month (ie. the
    first day of the month, and the first day of the next month).
    """
    lower_bound = date.replace(day=1)
    upper_bound = None

    if lower_bound.month < 12:
        upper_bound = lower_bound.replace(month=lower_bound.month + 1, day=1)
    else:
        upper_bound = lower_bound.replace(year=lower_bound.year + 1, month=1, day=1)

    return lower_bound, upper_bound


def is_date_between(
    date: datetime, lower_bound: datetime, upper_bound: datetime
) -> bool:
    """Return True if the given date is between the given bounds."""
    return date >= lower_bound and date < upper_bound
