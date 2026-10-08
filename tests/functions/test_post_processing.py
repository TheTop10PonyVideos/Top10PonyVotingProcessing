import pytest
from datetime import datetime
from functions.post_processing import (
    generate_top10_archive_records,
    generate_hm_archive_records,
    generate_sharable_records,
    generate_showcase_description,
    create_videos_desc,
)


def test_generate_top10_archive_records():
    top_10_records = [
        {
            "Title": "Example 1",
            "Percentage": "90.0000%",
            "Total Votes": "18",
            "URL": "https://example.com/1",
            "Notes": "",
        },
        {
            "Title": "Example 2",
            "Percentage": "80.0000%",
            "Total Votes": "16",
            "URL": "https://example.com/2",
            "Notes": "Tie broken randomly by computer",
        },
        {
            "Title": "Example 3",
            "Percentage": "80.0000%",
            "Total Votes": "16",
            "URL": "https://example.com/3",
            "Notes": "Tie broken randomly by computer",
        },
    ]

    videos_data = {
        "https://example.com/1": {
            "title": "Example 1",
            "uploader": "Uploader 1",
            "upload_date": datetime(2024, 4, 1),
        },
        "https://example.com/2": {
            "title": "Example 2",
            "uploader": "Uploader 2",
            "upload_date": datetime(2024, 4, 2),
        },
        "https://example.com/3": {
            "title": "Example 3",
            "uploader": "Uploader 3",
            "upload_date": datetime(2024, 4, 3),
        },
    }

    records = generate_top10_archive_records(top_10_records, videos_data)

    assert 3 == len(records)

    assert 2024 == records[0]["year"]
    assert 4 == records[0]["month"]
    assert 3 == records[0]["rank"]
    assert "https://example.com/3" == records[0]["link"]
    assert "Example 3" == records[0]["title"]
    assert "Uploader 3" == records[0]["channel"]
    assert "2024-04-03" == records[0]["upload date"]
    assert "" == records[0]["state"]
    assert "https://example.com/3" == records[0]["alternate link"]
    assert "" == records[0]["found"]
    assert "" == records[0]["notes"]
    assert "80.0000%" == records[0]["vote percentage"]

    assert 2024 == records[1]["year"]
    assert 4 == records[1]["month"]
    assert 2 == records[1]["rank"]
    assert "https://example.com/2" == records[1]["link"]
    assert "Example 2" == records[1]["title"]
    assert "Uploader 2" == records[1]["channel"]
    assert "2024-04-02" == records[1]["upload date"]
    assert "" == records[1]["state"]
    assert "https://example.com/2" == records[1]["alternate link"]
    assert "" == records[1]["found"]
    assert "" == records[1]["notes"]
    assert "80.0000%" == records[1]["vote percentage"]

    assert 2024 == records[2]["year"]
    assert 4 == records[2]["month"]
    assert 1 == records[2]["rank"]
    assert "https://example.com/1" == records[2]["link"]
    assert "Example 1" == records[2]["title"]
    assert "Uploader 1" == records[2]["channel"]
    assert "2024-04-01" == records[2]["upload date"]
    assert "" == records[2]["state"]
    assert "https://example.com/1" == records[2]["alternate link"]
    assert "" == records[2]["found"]
    assert "" == records[2]["notes"]
    assert "90.0000%" == records[2]["vote percentage"]

def test_generate_hm_archive_records():
    hm_records = [
        {
            "Title": "HM 1",
            "Percentage": "90.0000%",
            "Total Votes": "18",
            "URL": "https://example.com/1",
            "Notes": "",
        },
        {
            "Title": "HM 2",
            "Percentage": "80.0000%",
            "Total Votes": "16",
            "URL": "https://example.com/2",
            "Notes": "",
        },
    ]

    videos_data = {
        "https://example.com/1": {
            "title": "HM 1",
            "uploader": "Uploader 1",
            "upload_date": datetime(2024, 4, 1),
        },
        "https://example.com/2": {
            "title": "HM 2",
            "uploader": "Uploader 2",
            "upload_date": datetime(2024, 4, 2),
        },
    }

    records = generate_hm_archive_records(hm_records, videos_data)

    assert 2 == len(records)

    assert 2024 == records[0]["Year"]
    assert 4 == records[0]["Month"]
    assert "https://example.com/2" == records[0]["Original Link"]
    assert "HM 2" == records[0]["Title"]
    assert "Uploader 2" == records[0]["Channel"]
    assert "2024-04-02" == records[0]["Upload Date"]
    assert "" == records[0]["State"]
    assert "https://example.com/2" == records[0]["Alternate link"]
    assert "" == records[0]["Found"]
    assert "" == records[0]["Notes"]

    assert 2024 == records[1]["Year"]
    assert 4 == records[1]["Month"]
    assert "https://example.com/1" == records[1]["Original Link"]
    assert "HM 1" == records[1]["Title"]
    assert "Uploader 1" == records[1]["Channel"]
    assert "2024-04-01" == records[1]["Upload Date"]
    assert "" == records[1]["State"]
    assert "https://example.com/1" == records[1]["Alternate link"]
    assert "" == records[1]["Found"]
    assert "" == records[1]["Notes"]

def test_generate_sharable_records():
    top_10_records = [
        {
            "Title": "Example 1",
            "Percentage": "90.0000%",
            "Votes": "18",
            "Max Votes": "20",
            "Total Voters": "20",
            "URL": "https://example.com/1",
            "Notes": "",
        },
        {
            "Title": "Example 2",
            "Percentage": "80.0000%",
            "Votes": "16",
            "Max Votes": "20",
            "Total Voters": "20",
            "URL": "https://example.com/2",
            "Notes": "Tie broken randomly by computer",
        },
        {
            "Title": "Example 3",
            "Percentage": "80.0000%",
            "Votes": "16",
            "Max Votes": "20",
            "Total Voters": "20",
            "URL": "https://example.com/3",
            "Notes": "Tie broken randomly by computer",
        },
    ]

    hm_records = [
        {
            "Title": "Example 4",
            "Percentage": "60.0000%",
            "Votes": "12",
            "Max Votes": "20",
            "Total Voters": "20",
            "URL": "https://example.com/4",
            "Notes": "Missed out on top 10 due to tie break",
        },
        {
            "Title": "Example 5",
            "Percentage": "50.0000%",
            "Votes": "10",
            "Max Votes": "20",
            "Total Voters": "20",
            "URL": "https://example.com/5",
            "Notes": "",
        },
    ]

    records = generate_sharable_records(top_10_records, hm_records)

    assert 5 == len(records)

    assert 1 == records[0]["Rank"]
    assert "Example 1" == records[0]["Title"]
    assert (
        '=VLOOKUP("https://example.com/1", IMPORTRANGE("https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit", "top10!D:I"), 6, FALSE)'
        == records[0]["Link"]
    )
    assert "18" == records[0]["Votes"]
    assert "90.0000%" == records[0]["Popularity"]
    assert "20" == records[0]["Total Voters"]
    assert "" == records[0]["Notes"]

    assert 2 == records[1]["Rank"]
    assert "Example 2" == records[1]["Title"]
    assert (
        '=VLOOKUP("https://example.com/2", IMPORTRANGE("https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit", "top10!D:I"), 6, FALSE)'
        == records[1]["Link"]
    )
    assert "16" == records[1]["Votes"]
    assert "80.0000%" == records[1]["Popularity"]
    assert "20" == records[1]["Total Voters"]
    assert "Tie broken randomly by computer" == records[1]["Notes"]

    assert 3 == records[2]["Rank"]
    assert "Example 3" == records[2]["Title"]
    assert (
        '=VLOOKUP("https://example.com/3", IMPORTRANGE("https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit", "top10!D:I"), 6, FALSE)'
        == records[2]["Link"]
    )
    assert "16" == records[2]["Votes"]
    assert "80.0000%" == records[2]["Popularity"]
    assert "20" == records[2]["Total Voters"]
    assert "Tie broken randomly by computer" == records[2]["Notes"]

    assert "HM" == records[3]["Rank"]
    assert "Example 4" == records[3]["Title"]
    assert (
        '=VLOOKUP("https://example.com/4", IMPORTRANGE("https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit", "Honorable Mentions!C:I"), 6, FALSE)'
        == records[3]["Link"]
    )
    assert "12" == records[3]["Votes"]
    assert "60.0000%" == records[3]["Popularity"]
    assert "20" == records[3]["Total Voters"]
    assert (
        "HM. Missed out on top 10 due to tie break" == records[3]["Notes"]
    )

    assert "HM" == records[4]["Rank"]
    assert "Example 5" == records[4]["Title"]
    assert (
        '=VLOOKUP("https://example.com/5", IMPORTRANGE("https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit", "Honorable Mentions!C:I"), 6, FALSE)'
        == records[4]["Link"]
    )
    assert "10" == records[4]["Votes"]
    assert "50.0000%" == records[4]["Popularity"]
    assert "20" == records[4]["Total Voters"]
    assert "HM" == records[4]["Notes"]

def test_generate_showcase_description():
    top_10_records = [
        {
            "Title": "Top 10 Video 1",
            "Percentage": "90.0000%",
            "Total Votes": "18",
            "URL": "https://example.com/1",
            "Notes": "",
        },
        {
            "Title": "Top 10 Video 2",
            "Percentage": "80.0000%",
            "Total Votes": "16",
            "URL": "https://example.com/2",
            "Notes": "Tie broken randomly by computer",
        },
        {
            "Title": "Top 10 Video 3",
            "Percentage": "80.0000%",
            "Total Votes": "16",
            "URL": "https://example.com/3",
            "Notes": "Tie broken randomly by computer",
        },
    ]

    hm_records = [
        {
            "Title": "Honorable mention 1",
            "Percentage": "60.0000%",
            "Total Votes": "12",
            "URL": "https://example.com/hm1",
            "Notes": "Missed out on top 10 due to tie break",
        },
        {
            "Title": "Honorable mention 2",
            "Percentage": "50.0000%",
            "Total Votes": "10",
            "URL": "https://example.com/hm2",
            "Notes": "",
        },
    ]

    history_records = {
        "1 year ago": [
            {
                "Title": "History 1",
                "Percentage": "10.0000%",
                "Total Votes": "2",
                "URL": "https://example.com/hist1",
                "Notes": "",
            },
            {
                "Title": "History 2",
                "Percentage": "10.0000%",
                "Total Votes": "2",
                "URL": "https://example.com/hist2",
                "Notes": "",
            },
        ],
        "3 years ago": [
            {
                "Title": "History 3",
                "Percentage": "10.0000%",
                "Total Votes": "2",
                "URL": "https://example.com/hist3",
                "Notes": "",
            },
            {
                "Title": "History 4",
                "Percentage": "10.0000%",
                "Total Votes": "2",
                "URL": "https://example.com/hist4",
                "Notes": "",
            },
        ],
        "5 years ago": [
            {
                "Title": "History 5",
                "Percentage": "10.0000%",
                "Total Votes": "2",
                "URL": "https://example.com/hist5",
                "Notes": "",
            },
            {
                "Title": "History 6",
                "Percentage": "10.0000%",
                "Total Votes": "2",
                "URL": "https://example.com/hist6",
                "Notes": "",
            },
        ],
    }

    top_10_videos_data = {
        "https://example.com/1": {
            "title": "Top 10 Video 1",
            "uploader": "Uploader 1",
            "upload_date": datetime(2024, 4, 1),
        },
        "https://example.com/2": {
            "title": "Top 10 Video 2",
            "uploader": "Uploader 2",
            "upload_date": datetime(2024, 4, 2),
        },
        "https://example.com/3": None,
    }

    hm_videos_data = {
        "https://example.com/hm1": {
            "title": "Honorable mention 1",
            "uploader": "Uploader HM1",
            "upload_date": datetime(2024, 4, 1),
        },
        "https://example.com/hm2": {
            "title": "Honorable mention 2",
            "uploader": "Uploader HM2",
            "upload_date": datetime(2024, 4, 2),
        },
    }

    history_videos_data = {
        "https://example.com/hist1": {
            "title": "History 1",
            "uploader": "Uploader H1",
            "upload_date": datetime(2024, 4, 1),
        },
        "https://example.com/hist2": {
            "title": "History 2",
            "uploader": "Uploader H2",
            "upload_date": datetime(2024, 4, 2),
        },
        "https://example.com/hist3": {
            "title": "History 3",
            "uploader": "Uploader H3",
            "upload_date": datetime(2024, 4, 3),
        },
        "https://example.com/hist4": {
            "title": "History 4",
            "uploader": "Uploader H4",
            "upload_date": datetime(2024, 4, 4),
        },
        "https://example.com/hist5": {
            "title": "History 5",
            "uploader": "Uploader H5",
            "upload_date": datetime(2024, 4, 5),
        },
        "https://example.com/hist6": {
            "title": "History 6",
            "uploader": "Uploader H6",
            "upload_date": datetime(2024, 4, 6),
        },
    }

    desc = generate_showcase_description(
        top_10_records,
        hm_records,
        history_records,
        top_10_videos_data,
        hm_videos_data,
        history_videos_data,
        True,
    )

    # Top 10 Video 3 had no video data, but it should still appear in the
    # description as the function will automatically source the data from
    # the supplied record. However, it won't have an uploader.
    assert "Be sure to check out the videos in the description below! " in desc
    assert "Top 10 Video 1" in desc
    assert "https://example.com/1" in desc
    assert "Uploader 1" in desc
    assert "Top 10 Video 2" in desc
    assert "https://example.com/2" in desc
    assert "Uploader 2" in desc
    assert "Top 10 Video 3" in desc
    assert "https://example.com/3" in desc

    assert "The Top 10 Pony Videos of April 2023" in desc
    assert "The Top 10 Pony Videos of April 2021" in desc
    assert "The Top 10 Pony Videos of April 2019" in desc

    assert "Fuck YouTube" in desc

def test_create_videos_desc():
    records = [
        {
            "Title": "Honorable mention 1",
            "Percentage": "20.0000%",
            "Total Votes": "2",
            "URL": "https://example.com/hm1",
            "Notes": "",
        },
        {
            "Title": "Honorable mention 2",
            "Percentage": "10.0000%",
            "Total Votes": "1",
            "URL": "https://example.com/hm2",
            "Notes": "",
        },
    ]

    videos_data = {
        "https://example.com/hm1": {
            "title": "Honorable mention 1",
            "uploader": "Uploader 1",
            "upload_date": datetime(2024, 4, 1),
        },
        "https://example.com/hm2": {
            "title": "Honorable mention 2",
            "uploader": "Uploader 2",
            "upload_date": datetime(2024, 4, 2),
        },
    }

    desc = create_videos_desc(records, videos_data)

    assert (
        desc ==
        """○ Honorable mention 1
https://example.com/hm1
Uploader 1

○ Honorable mention 2
https://example.com/hm2
Uploader 2
"""
    )
