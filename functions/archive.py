"""Functions for operating on the master archive spreadsheet[1], a Google Sheets
document which stores historical voting data and is manually updated after each
new Top 10 Pony Videos showcase. For ease of access, the application typically
downloads a local copy of the spreadsheet and reads from that.

    [1]: https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E
"""

import csv, requests
from pathlib import Path
from functions.messages import suc, inf
from classes.typing import ArchiveRecord
from data.globals import (
    honorable_mentions_csv_url,
    local_honorable_mentions_csv_path,
    local_top_10_archive_csv_path,
    top_10_archive_csv_url
)

def load_top_10_master_archive(local_first = True) -> list[ArchiveRecord]:
    """Load a copy of the Top 10 Pony Videos List spreadsheet. Load a local copy if local_first is True,
    or if there's no such copy on the filesystem, export one from Google Sheets and
    save it first.

    The archive is returned as a list of records, with the key names being the
    field headers of the master archive file."""

    archive_records = None
    while True:
        try:
            if not local_first:
                local_first = True
                raise Exception

            # Try to load the local copy of the master archive spreadsheet
            with Path(local_top_10_archive_csv_path).open(
                "r", encoding="utf-8"
            ) as file:
                inf("Loading local copy of master Top 10 Pony Videos archive...")
                reader = csv.DictReader(file)
                reader.fieldnames = [field_name.lower().replace(" ", "_") for field_name in reader.fieldnames]
                archive_records = [record for record in reader]
                break
        except Exception:
            inf(
                "Downloading a copy of the master Top 10 Pony Videos archive..."
            )
            response = requests.get(top_10_archive_csv_url)
            response.encoding = "utf-8"
            Path(local_top_10_archive_csv_path).write_text(
                response.text, encoding="utf-8"
            )
            suc(
                f"Local copy of master Top 10 Pony Videos archive saved to {local_top_10_archive_csv_path}."
            )

    return archive_records


def load_honorable_mentions_archive(local_first = True) -> list[ArchiveRecord]:
    """Load a copy of the honorable mentions spreadsheet. Load a local copy if local_first is True,
    or if there's no local copy on the filesystem, export one from Google Sheets and
    save it first.

    The archive is returned as a list of records, with the key names being the
    same field headers of the master archive file."""

    archive_records = None
    while True:
        try:
            if not local_first:
                local_first = True
                raise Exception

            # Try to load the local copy of the honorable mentions archive spreadsheet
            with Path(local_honorable_mentions_csv_path).open(
                "r", encoding="utf-8"
            ) as file:
                inf("Loading local copy of honorable mentions archive...")
                reader = csv.DictReader(file)
                reader.fieldnames[reader.fieldnames.index("Original Link")] = "link"
                reader.fieldnames = [field_name.lower().replace(" ", "_") for field_name in reader.fieldnames]
                archive_records = [record for record in reader]
                break
        except Exception:
            inf(
                "Downloading a copy of the honorable mentions archive one..."
            )
            response = requests.get(honorable_mentions_csv_url)
            response.encoding = "utf-8"
            Path(local_honorable_mentions_csv_path).write_text(
                response.text, encoding="utf-8"
            )
            suc(
                f"Local copy of honorable mentions archive saved to {local_honorable_mentions_csv_path}."
            )

    return archive_records


def merge_aliased_creators(archive: list[ArchiveRecord], aliases: dict[str, list[str]]) -> list[str]:
    """Given a list of archive records (e.g. the master archive), and a
    dictionary which maps canonical creator names to a list of their possible
    aliases, merge any aliased creators with their aliases and treat them as a
    single creator. This modifies the archive object in-place. A list of all
    merged creators is also returned.

    Example, if "AgrolChannel" maps to "ForgaLorga", the resulting list of
    archive records will attribute all of ForgaLorga's videos to AgrolChannel,
    and "AgrolChannel" will be in the returned list of merged creators."""
    alias_to_canon = {}
    for canon, alias_list in aliases.items():
        for alias in alias_list:
            alias_to_canon[alias] = canon

    merged_creators = []
    for record in archive:
        creator = record["channel"]
        if creator not in alias_to_canon:
            continue

        canon = alias_to_canon[creator]
        record["channel"] = canon

        if canon not in merged_creators:
            merged_creators.append(canon)

    return merged_creators
