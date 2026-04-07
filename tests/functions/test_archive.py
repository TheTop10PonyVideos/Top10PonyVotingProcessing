import pytest
from pandas import DataFrame
from functions.archive import merge_aliased_creators, convert_ancient_to_master_format
from classes.typing import ArchiveRecord

def test_merge_aliased_creators():
    aliases = {
        "Creator A": ["Alias A1", "Alias A2"],
        "Creator B": ["Alias B"],
    }

    archive: list[ArchiveRecord] = [
        {
            "year": "2025",
            "month": "4",
            "rank": "1",
            "link": "https://example.com/1",
            "title": "Example 1",
            "channel": "Creator A",
            "upload_date": "2025-04-01",
            "state": "",
            "alternate_link": "",
            "found": "found",
            "notes": "",
            "Voters": "60",
        },
        {
            "year": "2025",
            "month": "5",
            "rank": "2",
            "link": "https://example.com/2",
            "title": "Example 2",
            "channel": "Creator B",
            "upload_date": "2025-05-02",
            "state": "",
            "alternate_link": "",
            "found": "found",
            "notes": "",
            "Voters": "50",
        },
        {
            "year": "2025",
            "month": "6",
            "rank": "3",
            "link": "https://example.com/3",
            "title": "Example 3",
            "channel": "Creator C",
            "upload_date": "2025-06-03",
            "state": "",
            "alternate_link": "",
            "found": "found",
            "notes": "",
            "Voters": "40",
        },
        {
            "year": "2025",
            "month": "7",
            "rank": "4",
            "link": "https://example.com/4",
            "title": "Example 4",
            "channel": "Alias A1",
            "upload_date": "2025-07-04",
            "state": "",
            "alternate_link": "",
            "found": "found",
            "notes": "",
            "Voters": "30",
        },
        {
            "year": "2025",
            "month": "8",
            "rank": "5",
            "link": "https://example.com/5",
            "title": "Example 5",
            "channel": "Alias A2",
            "upload_date": "2025-08-05",
            "state": "",
            "alternate_link": "",
            "found": "found",
            "notes": "",
            "Voters": "20",
        },
        {
            "year": "2025",
            "month": "9",
            "rank": "6",
            "link": "https://example.com/6",
            "title": "Example 6",
            "channel": "Alias B",
            "upload_date": "2025-09-06",
            "state": "",
            "alternate_link": "",
            "found": "found",
            "notes": "",
            "Voters": "10",
        },
    ]

    merged_creators = merge_aliased_creators(archive, aliases)

    assert len(archive) == 6
    assert archive[0]["channel"] == "Creator A"
    assert archive[1]["channel"] == "Creator B"
    assert archive[2]["channel"] == "Creator C"
    assert archive[3]["channel"] == "Creator A"
    assert archive[4]["channel"] == "Creator A"
    assert archive[5]["channel"] == "Creator B"

    assert len(merged_creators) == 2
    assert merged_creators[0] == "Creator A"
    assert merged_creators[1] == "Creator B"


def test_convert_ancient_to_master_format():
    df = DataFrame({
        "title": ["Ancient 1", "Ancient 2", "Ancient 3", "Ancient 4"],
        "upload_date YMD": ["2011-04-01", "2010-10-10", "2010-07-10", None],
        "Original link": ["https://example.com/1", "https://example.com/2", "https://example.com/3", "https://example.com/4"],
        "last status": ["", "Deleted", "Unavailable", ""],
        "Current link": ["https://example.com/4", "https://example.com/5", "https://example.com/6", "https://example.com/7"],
        "Last known channel name": ["Uploader A", "Uploader B", "Uploader C", "Uploader D"],
        "Notes": ["", "", "example", "no upload date"]
    })

    records = convert_ancient_to_master_format(df)

    assert len(records) == 3
    assert records[0]["year"] == "2011"
    assert records[0]["month"] == "4"
    assert records[0]["title"] == "Ancient 1"
    assert records[1]["year"] == "2010"
    assert records[1]["link"] == "https://example.com/2"
    assert records[1]["upload_date"] == "2010-10-10"
    assert records[1]["state"] == "Deleted"
    assert records[2]["channel"] == "Uploader C"
    assert records[2]["alternate_link"] == "https://example.com/6"
