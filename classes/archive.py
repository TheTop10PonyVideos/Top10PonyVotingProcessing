from typing import TypedDict

# URL to the downloadable CSV export of the master Top 10 Pony Videos List.
top_10_archive_csv_url = "https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/export?format=csv"

# URL to the downloadable CSV export of the honorable mentions list.
honorable_mentions_csv_url = "https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/export?format=csv&gid=841236474#gid=841236474"

# Path to a local copy of the master Top 10 Pony Videos List (in CSV format).
local_top_10_archive_csv_path = "data/top_10_master_archive.csv"

# Path to a local copy of the honorable mentions list (in CSV format).
local_honorable_mentions_csv_path = "data/honorable_mentions_archive.csv"

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
