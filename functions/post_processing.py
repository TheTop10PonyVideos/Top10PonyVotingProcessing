import csv
from datetime import datetime
from pathlib import Path
from functions.general import get_freq_table
from functions.date import get_most_common_month_year, rel_anni_date_to_abs
from functions.messages import suc, inf, err

# URL of Flynn's master archive of all Top 10 Pony Videos results, referenced by
# some of the output spreadsheets.
MASTER_ARCHIVE_URL = "https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit"


def generate_top10_archive_records(
    top_10_records: list[dict], videos_data: dict
) -> list[dict]:
    """Given a list of top 10 records and a collection of accompanying video
    data indexed by video URL, generate a list of data records in the format
    used by [Flynn's Top 10 Pony Videos List][1].

    [1]: https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E
    """

    records = []
    # Note: records created in reverse order as per the convention used in the
    # master archive spreadsheet.
    for i, top_10_record in enumerate(reversed(top_10_records)):
        rank = len(top_10_records) - i
        url = top_10_record["URL"]
        video_data = videos_data[url]

        year = ""
        month = ""
        channel = ""
        upload_date = ""

        # TODO: Warn the user if video data is not available for some reason.
        if video_data is not None:
            year = video_data["upload_date"].year
            month = video_data["upload_date"].month
            channel = video_data["uploader"]
            upload_date = video_data["upload_date"].strftime("%Y-%m-%d")

        record = {
            "year": year,
            "month": month,
            "rank": rank,
            "link": url,
            "title": top_10_record["Title"],
            "channel": channel,
            "upload date": upload_date,
            "state": "",
            "alternate link": url,
            "found": "",
            "notes": "",
        }

        records.append(record)

    return records


def generate_hm_archive_records(
    hm_records: list[dict], videos_data: dict
) -> list[dict]:
    """Given a list of honorable mention records and a collection of
    accompanying video data indexed by video URL, generate a list of data
    records in the format used by [Flynn's Top 10 Pony Videos List][1].

    [1]: https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E
    """

    records = []
    # Note: records created in reverse order as per the convention used in the
    # master archive spreadsheet.
    for i, hm_record in enumerate(reversed(hm_records)):
        url = hm_record["URL"]
        video_data = videos_data[url]

        year = ""
        month = ""
        channel = ""
        upload_date = ""

        # TODO: Warn the user if video data is not available for some reason.
        if video_data is not None:
            year = video_data["upload_date"].year
            month = video_data["upload_date"].month
            channel = video_data["uploader"]
            upload_date = video_data["upload_date"].strftime("%Y-%m-%d")

        record = {
            "Year": year,
            "Month": month,
            "Original Link": url,
            "Title": hm_record["Title"],
            "Channel": channel,
            "Upload Date": upload_date,
            "State": "",
            "Alternate link": url,
            "Found": "",
            "Notes": "",
        }

        records.append(record)

    return records


def generate_sharable_records(
    top_10_records: list[dict], hm_records: list[dict]
) -> list[dict]:
    """Given a list of top 10 records and a list of honorable mention records,
    generate a list of data records in the format used by the sharable
    spreadsheet included with each Top 10 Pony Videos showcase ([example from
    February 2024][2]).

    [2]: https://docs.google.com/spreadsheets/d/1CCXeLR18mdDx6T2wQcxjTW-LRauTNFmG88OKvfSHy_M
    """

    # Probably shouldn't do this, but since one of the fields requested by the
    # sharable spreadsheet is the total number of voters, we can
    # reverse-engineer that figure from votes and percentage:
    percentage = float(top_10_records[0]["Percentage"].strip("%"))
    votes = int(top_10_records[0]["Total Votes"])
    total_voters = round((100 * votes) / percentage)

    records = []

    for i, top_10_record in enumerate(top_10_records):
        rank = i + 1
        record = {
            "Rank": rank,
            "Title": top_10_record["Title"],
            "Link": f'=VLOOKUP("{top_10_record["URL"]}", IMPORTRANGE("{MASTER_ARCHIVE_URL}", "top10!D:I"), 6, FALSE)',
            "Votes": top_10_record["Total Votes"],
            "Popularity": top_10_record["Percentage"],
            "Total voters": total_voters,
            "Notes": top_10_record["Notes"],
        }

        records.append(record)

    for hm_record in hm_records:
        hm_notes = "HM"
        if hm_record["Notes"].strip() != "":
            hm_notes = f'{hm_notes}. {hm_record["Notes"]}'

        record = {
            "Rank": "HM",
            "Title": hm_record["Title"],
            "Link": f'=VLOOKUP("{hm_record["URL"]}", IMPORTRANGE("{MASTER_ARCHIVE_URL}", "Honorable Mentions!C:I"), 6, FALSE)',
            "Votes": hm_record["Total Votes"],
            "Popularity": hm_record["Percentage"],
            "Total voters": total_voters,
            "Notes": hm_notes,
        }

        records.append(record)

    return records


def generate_top10_archive_csv(records: list[dict], filename: str):
    """Given a list of Top 10 archive records, write them to a CSV file in a
    tabular format."""
    csv_path = Path(filename)

    if len(records) != 10:
        raise ValueError(
            f"Cannot generate top 10 archive CSV: {len(records)} videos were found, but there should be exactly 10"
        )

    header = [
        "year",
        "month",
        "rank",
        "link",
        "title",
        "channel",
        "upload date",
        "state",
        "alternate link",
        "found",
        "notes",
    ]

    for record in records:
        if len(record) != len(header):
            raise Exception(
                f"Cannot generate top 10 archive CSV; header has {len(header)} values but {len(record)} record values were given"
            )

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        csv_writer = csv.DictWriter(file, fieldnames=header)
        csv_writer.writeheader()
        csv_writer.writerows(records)


def generate_hm_archive_csv(records: list[dict], filename: str):
    """Given a list of honorable mention archive records, write them to a CSV
    file in a tabular format."""
    csv_path = Path(filename)

    header = [
        "Year",
        "Month",
        "Original Link",
        "Title",
        "Channel",
        "Upload Date",
        "State",
        "Alternate link",
        "Found",
        "Notes",
    ]

    for record in records:
        if len(record) != len(header):
            raise Exception(
                f"Cannot generate honorable mentions archive CSV; header has {len(header)} values but {len(record)} record values were given"
            )

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        csv_writer = csv.DictWriter(file, fieldnames=header)
        csv_writer.writeheader()
        csv_writer.writerows(records)


def generate_sharable_csv(records: list[dict], filename: str):
    """Given a list of sharable spreadsheet records, write them to a CSV file in
    a tabular format."""
    csv_path = Path(filename)
    header = ["Rank", "Title", "Link", "Votes", "Popularity", "Total voters", "Notes"]

    for record in records:
        if len(record) != len(header):
            raise Exception(
                f"Cannot generate sharable CSV; header has {len(header)} values but {len(record)} record values were given"
            )

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        csv_writer = csv.DictWriter(file, fieldnames=header)
        csv_writer.writeheader()
        csv_writer.writerows(records)


def generate_showcase_description(
    top_10_records: list[dict],
    hm_records: list[dict],
    history_records: dict[dict],
    top_10_videos_data: dict,
    hm_videos_data: dict,
    history_videos_data: dict,
    silent: bool = False,
) -> str:
    """Generate the description for the showcase video ([example from February
    2024][3]).

    The showcase description has 3 sections: the top 10 videos, honorable
    mentions, and a history section. To populate each, records must be supplied
    for each of those sections, along with accompanying video data for each URL
    in each section.

    [3]: https://www.youtube.com/watch?v=JOcVLEL-bgg
    """

    # Guess the voting month and year from the upload dates of the top 10
    # videos.
    upload_dates = [
        data["upload_date"]
        for url, data in top_10_videos_data.items()
        if data is not None
    ]
    upload_month, upload_year, is_unanimous = get_most_common_month_year(upload_dates)
    upload_date = datetime(upload_year, upload_month, 1)
    upload_month_year_str = upload_date.strftime("%B %Y")

    if not silent:
        inf(
            f"Assuming showcase date of {upload_month_year_str} based on most common upload month and year."
        )

    # Define various text strings used in the description.
    opening = "Be sure to check out the videos in the description below! The Top 10 Pony Videos is a long-running project to document and showcase the most popular My Little Pony videos in the brony community. Videos featured on the list are voted upon during a week-long voting process at the beginning of each month. This project has been active every single month since 2011!"

    project_links = {
        "Website": "https://www.thetop10ponyvideos.com/",
        "Discord server": "https://www.thetop10ponyvideos.com/discord",
    }

    sharable_links = {
        "Spreadsheet": "[ADD SHARABLE SPREADSHEET LINK HERE]",
        "YouTube playlist": "[ADD PLAYLIST LINK HERE]",
    }

    disclosures = "Full disclosures: Any placement of tied videos was determined randomly by computer."

    licensing = """
Top 10 Theme music: "Back Again (Original Mix)" by Archie
Get it here! https://mrarchie.bandcamp.com/track/back-again-original-mix
Used under Creative Commons license.
https://creativecommons.org/licenses/by-sa/3.0/"""

    mandatory_swearing = "Mandatory swearing to help avoid being wrongly blacklisted as MFK: Fuck YouTube. https://www.youtube.com/watch?v=h3l_c_ei6CQ"

    # Build the description from the text strings.
    desc = f"{opening}\n\n\n"

    for link_text, url in project_links.items():
        desc += f"{link_text}:\n"
        desc += f"► {url}\n"

    desc += "\n\n"
    desc += "► VIDEO LINKS:\n\n"

    for link_text, url in sharable_links.items():
        desc += f"• {link_text}: {url}\n"

    desc += "\n"

    # Add the top 10, honorable mentions, and history lists. Note that the top
    # 10 URLs are listed in reverse order of popularity, to match how they're
    # presented in the video.
    videos_desc = create_videos_desc(
        reversed(top_10_records), top_10_videos_data, silent
    )
    hm_desc = create_videos_desc(hm_records, hm_videos_data, silent)
    history_desc = create_history_desc(
        history_records, history_videos_data, upload_date, silent
    )

    desc += f"{videos_desc}\n\n"
    desc += "► Honorable mentions:\n\n"
    desc += f"{hm_desc}\n\n"
    desc += f"{history_desc}\n\n"
    desc += f"{disclosures}\n\n"
    desc += f"{licensing}\n\n"
    desc += f"{mandatory_swearing}\n"

    return desc


def create_videos_desc(
    records: list[dict], videos_data: dict, silent: bool = True
) -> str:
    """Given a list of top 10 records and a collection of video data indexed by
    URL, generate a videos list for the description. This also works for the
    Honorable mentions records."""

    video_descs = []

    for record in records:
        video_data = videos_data[record["URL"]]

        # Create a barebones video description based on what we know about it
        # from the calculated Top 10 spreadsheet.
        video_desc = f'○ {record["Title"]}\n'
        video_desc += f'{record["URL"]}\n'

        # Warn the user if we didn't have any video data for this video.
        if video_data is None:
            if not silent:
                err(
                    f'WARNING: No video data available for URL {record["URL"]}. The title and URL have been added to the showcase description based on the entry in the calculated Top 10 spreadsheet, but uploader information is not available.'
                )
        else:
            # We do have video data, so create a full description.
            video_desc = f'○ {video_data["title"]}\n'
            video_desc += f'{record["URL"]}\n'
            video_desc += f'{video_data["uploader"]}\n'

        video_descs.append(video_desc)

    return "\n".join(video_descs)


def create_history_desc(
    records: dict[dict], videos_data: dict, from_date: datetime, silent: bool = True
) -> str:
    """Given a collection of history records and a collection of video data
    indexed by URL, generate a history section for the description. The
    collection should be a dictionary indexed by relative dates of the form
    "N years ago"."""

    anni_descs = []

    for rel_anni_date, video_records in records.items():
        abs_anni_date = rel_anni_date_to_abs(rel_anni_date, from_date)
        history_month_year = abs_anni_date.strftime("%B %Y")
        heading = f"► The Top 10 Pony Videos of {history_month_year}"
        link_placeholder = "[ADD SHOWCASE LINK HERE]"

        anni_desc = (
            heading
            + "\n\n"
            + link_placeholder
            + "\n\n"
            + create_videos_desc(video_records, videos_data, silent)
        )
        anni_descs.append(anni_desc)

    history_desc = "\n".join(anni_descs)

    return history_desc
