"""Functions related to processing the votes CSV."""

import pandas as pd
from functions.date import format_votes_csv_timestamp
from functions.url import (
    is_youtube_url,
    is_derpibooru_url,
    normalize_youtube_url,
    normalize_derpibooru_url,
)
from classes.voting import Ballot, Vote, Video
from classes.fetcher import Fetcher
from classes.exceptions import (
    VideoUnavailableError,
    UnsupportedHostError,
    SchemaValidationError,
)


def load_votes_csv(csv_file_path_str: str) -> pd.DataFrame:
    """Given the path to a CSV file containing votes, load the votes,
    and return them in a dataframe."""
    return pd.read_csv(csv_file_path_str, header=0, keep_default_na=False)


def normalize_url(url: str):
    url = url.strip()

    if not url:
        return url

    if '://' not in url:
        url = 'https://' + url

    if is_youtube_url(url):
        url, _ = normalize_youtube_url(url)
    elif is_derpibooru_url(url):
        url = normalize_derpibooru_url(url)
    
    return url


def normalize_voting_data(df: pd.DataFrame) -> pd.DataFrame:
    """Given raw voting data, replace all of the URLs with
    "normalized" forms, such that different forms of the same URL become
    identical. This makes the output neater and prevents accidental
    undercounting.

    The data is assumed to be from the "unshifted" version of the voting data
    (ie. the voting CSV as obtained from Google Forms)."""
    normalized = df.copy()
    normalized.iloc[:, 1:] = df.iloc[:, 1:].map(normalize_url)
    normalized.columns = ['Timestamp'] + [''] * (len(df.columns) - 1)

    return normalized


def process_voting_data(df: pd.DataFrame) -> list[Ballot]:
    """Process the data from a (unshifted) votes CSV into a list of ballots.

    As a validity check, the header row of a votes CSV is required to begin with
    a "Timestamp" cell.
    """
    if df.columns[0].strip() != "Timestamp":
        raise ValueError(
            'Cannot process votes CSV; header row is invalid. The first cell must be the string "Timestamp"'
        )
    
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%m/%d/%Y %H:%M:%S')

    ballots: pd.Series = df.apply(process_votes_csv_row, axis=1)
    return ballots.to_list()


def process_votes_csv_row(row: pd.Series) -> Ballot:
    """Process a data row of a votes CSV into a Ballot object."""
    timestamp = row['Timestamp']

    vote_cells = row.iloc[1:].str.strip()
    votes = vote_cells[vote_cells != ''].map(Vote).to_list()

    return Ballot(timestamp, votes)


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

            video = Video()

            try:
                video.data = fetcher.fetch(vote.url)
            except UnsupportedHostError:
                video.annotations.add("UNSUPPORTED HOST")
            except VideoUnavailableError:
                video.annotations.add("VIDEO UNAVAILABLE")
            except Exception as e:
                video.annotations.add("COULD NOT FETCH")

            # Validate the fetched data to ensure it has all the fields we need
            # for our checks. If it doesn't, this might mean that the fetch
            # service needs updating to provide all required fields.
            if video.data is not None:
                missing_fields = validate_video_data(video.data)
                if len(missing_fields) > 0:
                    raise SchemaValidationError(
                        f'Error when validating video data for URL "{vote.url}"; the following fields are missing: {", ".join(missing_fields)}'
                    )

            videos[vote.url] = video

    return videos


def validate_video_data(data: dict) -> list[str]:
    """Check the given dictionary of video data and return a list of missing
    fields, if any. This helps ensure the fields we're interested in are always
    available."""
    required_fields = ["title", "uploader", "upload_date", "duration", "platform"]
    missing_fields = [field for field in required_fields if field not in data]

    return missing_fields


def generate_annotated_csv_data(
    ballots: list[Ballot], videos: dict[str, Video]
) -> pd.DataFrame:
    """Given a list of ballots, generate a dataframe that can be written
    to a CSV file, for use with the `calc.py` calculation script. The output
    resembles the input CSV, but with an additional column inserted after each
    URL column, in which the annotations for each vote are written next to each
    URL.
    """

    # Number of columns = 1 Timestamp column, plus 10 vote columns, multiplied
    # by 2 for annotation columns = 22
    num_cols = (1 + 10) * 2
    header_row = [''] * num_cols
    header_row[0] = "Timestamp"

    df = pd.DataFrame('', index=range(len(ballots)), columns=header_row)

    df['Timestamp'] = [format_votes_csv_timestamp(ballot.timestamp) for ballot in ballots]
    for r, ballot in enumerate(ballots):
        df.iloc[r, 0] = format_votes_csv_timestamp(ballot.timestamp)

        for c, vote in enumerate(ballot.votes, 1):
            video = videos[vote.url]
            # By convention, we include the voted-for URL if we weren't able
            # to obtain any video data for it - this makes it easier for the
            # user to check the URL themselves to see what's wrong.
            df.iloc[r, c * 2] = video["title"] if video.data is not None else vote.url

            if not vote.annotations.has_none():
                df.iloc[r, c * 2 + 1] = vote.annotations.get_label()

    return df


def shift_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Given a dataframe, return a dataframe of string columns where each
    cell of each row is succeeded by an empty cell. This results in a grid
    of cells interlaced with blank columns."""
    num_cols = len(df.columns) * 2
    cols = [''] * num_cols
    cols[::2] = df.columns

    shifted = pd.DataFrame('', index=df.index, columns=cols)
    shifted.iloc[:,::2] = df.astype(str)

    return shifted
