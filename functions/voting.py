"""Functions related to processing the votes CSV."""

import csv
from pathlib import Path
from datetime import datetime
from pytz import timezone
from functions.date import parse_votes_csv_timestamp, format_votes_csv_timestamp
from functions.url import is_youtube_url, normalize_youtube_url
from classes.voting import Ballot, Vote, Video
from classes.fetcher import Fetcher
from classes.exceptions import (
    VideoUnavailableError,
    UnsupportedHostError,
    SchemaValidationError,
)


def load_votes_csv(csv_file_path_str: str) -> list[list[str]]:
    """Given the path to a CSV file containing votes, load the votes, and return
    a list of data rows."""

    csv_file_path = Path(csv_file_path_str)
    rows = None
    with csv_file_path.open(encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file)
        rows = [row for row in csv_reader]

    return rows


def normalize_voting_data(rows: list[list[str]]) -> list[list[str]]:
    """Given a set of data rows from a voting CSV, replace all of the URLs with
    "normalized" forms, such that different forms of the same URL become
    identical. This makes the output neater and prevents accidental
    undercounting.

    The data is assumed to be from the "unshifted" version of the voting data
    (ie. the voting CSV as obtained from Google Forms)."""
    normalized_rows = [[cell for cell in row] for row in rows]

    for row_idx, row in enumerate(normalized_rows):
        # Skip header row
        if row_idx == 0:
            continue

        for cell_idx, cell in enumerate(row):
            # Skip "Timestamp" column
            if cell_idx == 0:
                continue

            if is_youtube_url(cell):
                normalized_rows[row_idx][cell_idx] = normalize_youtube_url(cell)

    return normalized_rows


def process_voting_data(csv_rows: list[list[str]]) -> list[Ballot]:
    """Process the data from a (unshifted) votes CSV into a list of ballots.

    As a validity check, the header row of a votes CSV is required to begin with
    a "Timestamp" cell.
    """
    header_row = csv_rows[0]
    if header_row[0].strip() != "Timestamp":
        raise ValueError(
            'Cannot process votes CSV; header row is invalid. The first cell must be the string "Timestamp"'
        )
    data_rows = csv_rows[1:]

    ballots = [process_votes_csv_row(row) for row in data_rows]

    return ballots


def process_votes_csv_row(row: list[str]) -> Ballot:
    """Process a data row of a votes CSV into a Ballot object."""
    timestamp = row[0]
    timestamp_dt = parse_votes_csv_timestamp(timestamp)

    vote_cells = row[1:]
    votes = [Vote(cell.strip()) for cell in vote_cells if cell.strip() != ""]

    return Ballot(timestamp_dt, votes)


def fetch_video_data_for_ballots(
    ballots: list[Ballot], fetcher: Fetcher
) -> dict[str, Video]:
    """For each video voted on, fetch the data for that video. Return the
    resulting set of fetch results, indexed by URL.

    If a video fails to fetch, include the reason for the failure (if known) in
    the fetch result. This helps with annotating the votes later.
    """
    videos = {}

    for ballot in ballots:
        for vote in ballot.votes:
            # Skip fetch if we already fetched data for this URL.
            #
            # TODO: It's possible for different URLs to resolve to the same
            # video, which could mean they're fetched more than once. Python's
            # `urllib.parse` library might be useful for normalizing URLs into a
            # consistent canonical form.
            if vote.url in videos:
                continue

            video = None
            try:
                data = fetcher.fetch(vote.url)
                video = Video(data)
            except UnsupportedHostError:
                video = Video()
                video.annotations.add("UNSUPPORTED HOST")
            except VideoUnavailableError:
                video = Video()
                video.annotations.add("VIDEO UNAVAILABLE")
            except Exception as e:
                video = Video()
                video.annotations.add("COULD NOT FETCH")

            # Validate the fetched data to ensure it has all the fields we need
            # for our checks. If it doesn't, this might mean that the fetch
            # service needs updating to provide all required fields.
            missing_fields = validate_video_data(data)
            if len(missing_fields) > 0:
                raise SchemaValidationError(
                    f'Error when validating video data for URL "{url}"; the following fields are missing: {", ".join(missing_fields)}'
                )

            videos[vote.url] = video

    return videos


def validate_video_data(data: dict) -> list[str]:
    """Check the given dictionary of video data and return a list of missing
    fields, if any. This helps ensure the fields we're interested in are always
    available."""
    required_fields = ["title", "uploader", "upload_date", "duration"]
    missing_fields = [field for field in required_fields if field not in data]

    return missing_fields


def generate_annotated_csv_data(
    ballots: list[Ballot], videos: dict[str, Video]
) -> list[list[str]]:
    """Given a list of ballots, generate a list of data rows that can be written
    to a CSV file, for use with the `calc.py` calculation script. The output
    resembles the input CSV, but with an additional column inserted after each
    URL column, in which the annotations for each vote are written next to each
    URL.
    """

    # Number of columns = 1 Timestamp column, plus 10 vote columns, multiplied
    # by 2 for annotation columns = 22
    num_cols = (1 + 10) * 2
    header_row = ["" for i in range(num_cols)]
    header_row[0] = "Timestamp"
    data_rows = []

    for ballot in ballots:
        data_row = [format_votes_csv_timestamp(ballot.timestamp), ""]
        for vote in ballot.votes:
            video = videos[vote.url]
            if video.data is not None:
                data_row.append(video["title"])
            else:
                # By convention, we include the voted-for URL if we weren't able
                # to obtain any video data for it - this makes it easier for the
                # user to check the URL themselves to see what's wrong.
                data_row.append(vote.url)

            if vote.annotations.has_none():
                data_row.append("")
            else:
                data_row.append(vote.annotations.get_label())

        # Pad any missing columns with empty cells
        while len(data_row) < num_cols:
            data_row.append("")

        data_rows.append(data_row)

    csv_rows = [header_row]
    for data_row in data_rows:
        csv_rows.append(data_row)

    return csv_rows


def shift_cells(row: list[str]) -> list[str]:
    """Given a list of string values, return a "shifted" list in which each cell
    is succeeded by an empty cell."""
    shifted_row = []
    for cell in row:
        shifted_row.extend([cell, ""])

    return shifted_row


def shift_columns(rows: list[list[str]]) -> list[list[str]]:
    """Given a list of rows of string values, return a list in which each cell
    of each row is succeeded by an empty cell. This results in a grid of cells
    interlaced with blank columns."""

    return [shift_cells(row) for row in rows]
