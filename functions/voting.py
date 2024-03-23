"""Functions related to processing the votes CSV."""

import csv
from pathlib import Path
from datetime import datetime
from pytz import timezone
from functions.date import parse_votes_csv_timestamp, format_votes_csv_timestamp
from classes.voting import Ballot, Vote, Video
from classes.fetcher import Fetcher
from classes.exceptions import VideoUnavailableError, UnsupportedHostError

def load_votes_csv(csv_file_path_str: str) -> list[Ballot]:
    """Given the path to a CSV file containing votes, load the votes, and return
    a list of corresponding Ballot objects.
    """

    csv_file_path = Path(csv_file_path_str)
    rows = None
    with csv_file_path.open() as csv_file:
        csv_reader = csv.reader(csv_file)
        rows = [row for row in csv_reader]

    ballots = process_votes_csv(rows)

    return ballots

def process_votes_csv(csv_rows: list[list[str]]) -> list[Ballot]:
    """Process the data in a votes CSV into a list of ballots.

    As a validity check, the header row of a votes CSV is required to begin with
    a "Timestamp" cell.
    """
    header_row = csv_rows[0]
    if header_row[0].strip() != 'Timestamp':
        raise ValueError('Cannot process votes CSV; header row is invalid. The first cell must be the string "Timestamp"')
    data_rows = csv_rows[1:]

    ballots = [process_votes_csv_row(row) for row in data_rows]

    return ballots

def process_votes_csv_row(row: list[str]) -> Ballot:
    """Process a data row of a votes CSV into a Ballot object."""
    timestamp = row[0]
    timestamp_dt = parse_votes_csv_timestamp(timestamp)

    vote_cells = row[1:]
    votes = [Vote(cell.strip()) for cell in vote_cells if cell.strip() != '']

    return Ballot(timestamp_dt, votes)


def fetch_video_data_for_ballots(ballots: list[Ballot], fetcher: Fetcher) -> dict[str, Video]:
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
                video.annotations.add('UNSUPPORTED HOST')
            except VideoUnavailableError:
                video = Video()
                video.annotations.add('VIDEO UNAVAILABLE')
            except Exception as e:
                video = Video()
                video.annotations.add('COULD NOT FETCH')
                
            videos[vote.url] = video

    return videos

def generate_annotated_csv_data(ballots: list[Ballot], videos: dict[str, Video]) -> list[list[str]]:
    """Given a list of ballots, generate a list of data rows that can be written
    to a CSV file, for use with the `calc.py` calculation script. The output
    resembles the input CSV, but with an additional column inserted after each
    URL column, in which the annotations for each vote are written next to each
    URL.
    """

    # TODO: This isn't the exact same timestamp format as the input CSV, as the
    # month, day, and hour may contain leading zeroes (the input CSV doesn't).
    # I'm not sure the timestamp actually matters for the calculation, though.

    # Number of columns = 1 Timestamp column, plus 10 vote columns, multiplied
    # by 2 for annotation columns = 22
    num_cols = (1 + 10) * 2
    header_row = ['' for i in range(num_cols)]
    header_row[0] = 'Timestamp'
    data_rows = []

    for ballot in ballots:
        data_row = [format_votes_csv_timestamp(ballot.timestamp), '']
        for vote in ballot.votes:
            video = videos[vote.url]
            if video.data is not None:
                data_row.append(video['title'])
            else:
                data_row.append('')
                
            if vote.annotations.has_none():
                data_row.append('')
            else:
                data_row.append(vote.annotations.get_label())

        # Pad any missing columns with empty cells
        while len(data_row) < num_cols:
            data_row.append('')

        data_rows.append(data_row)

    csv_rows = [header_row]
    for data_row in data_rows:
        csv_rows.append(data_row)

    return csv_rows
            
