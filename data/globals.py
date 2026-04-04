"""Module that contains global variables that may be needed in several project files"""

import os

# URL to the downloadable CSV export of the master Top 10 Pony Videos List.
top_10_archive_csv_url = "https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/export?format=csv"

# URL to the downloadable CSV export of the honorable mentions list.
honorable_mentions_csv_url = "https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/export?format=csv&gid=841236474#gid=841236474"

# Path to a local copy of the master Top 10 Pony Videos List (in CSV format).
local_top_10_archive_csv_path = "data/top_10_master_archive.csv"

# Path to a local copy of the honorable mentions list (in CSV format).
local_honorable_mentions_csv_path = "data/honorable_mentions_archive.csv"

# More convenient aliases for the various archives.
archives = {
    "master": {
        "local": local_top_10_archive_csv_path,
        "url": top_10_archive_csv_url,
    },
    "honorable": {
        "local": local_honorable_mentions_csv_path,
        "url": honorable_mentions_csv_url,
    },
    "ancient": {
        "local": "data/ancient_pony_videos.csv",
        "url": "https://docs.google.com/spreadsheets/d/1_kAxJhcbHLvE1YeyWHj2KjgOcgQMC84wDoavzeLkpx8/export?format=csv",
        "header_idx": 1
    },
}

ydl_opts = {
    "quiet": True,
    "no_warnings": True,
    "retries": 3,
    "sleep_interval": 2,
    "allowed_extractors": [
        "BiliBili",
        "Bluesky",
        "dailymotion",
        "Instagram",
        "lbry", # Odysee
        "Newgrounds",
        "twitter",
        "PeerTube", # pony.tube & pt.thishorsie.rocks
        "TikTok",
        "vimeo",
        "generic", # ytdlp may fall back to the generic extractor if another fails
    ],
}

# Previously, some twitter requests returned no data due to content being restricted
if os.path.exists("data/cookies.txt"):
    ydl_opts["cookiefile"] = "data/cookies.txt"
