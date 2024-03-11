"""Functions for checking the video upload date to ensure that it falls within
the month being voted on. The month being voted on is defined to be the
preceding month.

Example: If the current month is April 2024, then the month being
voted on is March 2024. Any video that was uploaded prior to March 1st 2024 is
considered too old. Any video that was uploaded after March 31st 2024 is
considered too new.

For the purpose of determining the exact time the month starts, this script uses
the Pacific/Kiribati timezone Etc/GMT-14, which as of writing is the earliest
timezone in the world.
"""

import calendar, csv, os
from datetime import datetime
from pytz import timezone
from modules import data_pulling

# Use the earliest possible global timezone to determine the current month. Once
# it is, say, January somewhere in the world, it is for everyone in respects to
# this script.
zone = timezone("Etc/GMT-14")


def get_preceding_month(tz: timezone) -> datetime:
    """Return an integer (1 to 12) representing the first day of the preceding
    month. For the purpose of deciding exactly when the month starts, a timezone
    must be supplied.
    """
    today = datetime.now(tz)
    month = today.month
    return month - 1 if month > 1 else 12


def get_month_bounds(month: int, tz: timezone) -> tuple[datetime, datetime]:
    """Given a month number, return the two dates that bound that month (ie. the
    first day of the month, and the first day of the next month).
    """
    today = datetime.now(tz)
    lower_bound = today.replace(month=month, day=1)
    upper_bound = None

    if month < 12:
        upper_bound = lower_bound.replace(month=lower_bound.month + 1, day=1)
    else:
        upper_bound = lower_bound.replace(year=lower_bound.year + 1, month=1, day=1)

    return lower_bound, upper_bound


def compare_date_to_bounds(
    date: datetime, lower_bound: datetime, upper_bound: datetime
) -> int:
    """Compare a given date against a pair of lower and upper bounds. Return -1
    if the date is earlier than the bounds, 1 if the date is later than the
    bounds, or 0 if the date falls within the bounds.
    """
    if date < lower_bound:
        return -1
    if date >= upper_bound:
        return 1
    return 0


def check_dates(video_urls_file_path: str, titles_file_path: str, output_file_path: str):
    """Given a CSV file containing video URLs, obtain the upload date for each
    URL, and annotate the column next to it if the upload date is too old or too
    new.
    """
    temp_output_file_path = "outputs/temp_outputs/processed_dates.csv"

    voting_month = get_preceding_month(zone)
    lower_date_bound, upper_date_bound = get_month_bounds(voting_month, zone)

    with (
        open(video_urls_file_path, "r", encoding="utf-8") as csv_video_urls,
        open(titles_file_path, "r", encoding="utf-8") as csv_titles,
        open(temp_output_file_path, "w", newline="", encoding="utf-8") as csv_output,
    ):
        reader_video_urls = csv.reader(csv_video_urls)
        reader_titles = csv.reader(csv_titles)
        writer = csv.writer(csv_output)

        rows_video_urls = [row for row in reader_video_urls]

        urls = []
        for row in rows_video_urls:
            urls.extend(data_pulling.get_video_urls(row))

        urls_to_metadata = data_pulling.get_urls_to_metadata(urls)

        for row_video_urls, row_titles in zip(rows_video_urls, reader_titles):
            for index, cell in enumerate(row_video_urls):
                if not cell in urls_to_metadata:
                    continue

                metadata = urls_to_metadata[cell]

                if metadata.upload_date is None:
                    print(
                        f"[UPLOAD DATE] ERROR: Could not obtain an upload date for {cell}. Proceeding without it."
                    )
                    continue

                upload_date = metadata.upload_date
                # Both YouTube and yt-dlp return upload dates in UTC, which is
                # considered a "naive" datetime as it lacks timezone
                # information. In order to perform a date comparison with our
                # lower and upper bounds, turn it into an "aware" date by
                # supplying a timezone.
                upload_date = upload_date.replace(tzinfo=zone)

                upload_date_comparison = compare_date_to_bounds(
                    upload_date, lower_date_bound, upper_date_bound
                )
                if upload_date_comparison == -1:
                    row_titles[index + 1] += "[VIDEO TOO OLD]"
                if upload_date_comparison == 1:
                    row_titles[index + 1] += "[VIDEO TOO NEW]"

            writer.writerow(row_titles)

    os.remove(output_file_path)
    os.rename(temp_output_file_path, output_file_path)
