import csv
from datetime import datetime
from pathlib import Path
from functions.services import get_fetcher
from functions.date import get_freq_table
from functions.messages import suc, inf, err
from classes.fetcher import Fetcher

# URL of Flynn's master archive of all Top 10 Pony Videos results, referenced by
# some of the output spreadsheets.
MASTER_ARCHIVE_URL = "https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit"

def fetch_videos_data(urls: list[str]) -> dict[str, dict]:
    """Given a list of video URLs, return a dictionary mapping each URL to its
    data."""
    fetcher = get_fetcher()

    videos_data = {}
    for url in urls:
        video_data = None
        try:
            video_data = fetcher.fetch(url)
        except Exception as e:
            err(f'WARNING: Could not fetch data for URL {url}')

        videos_data[url] = video_data

    return videos_data


def generate_archive_records(urls: str, videos_data: dict[str, dict]) -> list[dict]:
    """Given a list of video URLs and a dictionary mapping each URL to its data,
     generate a list of data records in the format used by [Flynn's Top 10 Pony
    Videos List][1].

    [1]: https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E
    """

    records = []
    # Note: records created in reverse order as per the convention used in the
    # master archive spreadsheet.
    for url in reversed(urls):
        data = videos_data[url]

        if data is None:
            err(f"WARNING: Unable to generate archive record for URL {url}; no data available. This video will not be represented in the output.")
            continue

        records.append(
            {
                'year': data['upload_date'].year,
                'month' :data['upload_date'].month,
                'rank': '',
                'link': url,
                'title': data['title'],
                'channel': data['uploader'],
                'upload date': data['upload_date'].strftime('%Y-%m-%d'),
                'state': '',
                'alternate link': url,
                'found': '',
                'notes': '',
            }
        )

    return records

def generate_sharable_records(urls: list[str], videos_data: dict[str, dict]) -> list[dict]:
    """Given a list of video URLs and a dictionary mapping each URL to its data,
    generate a list of data records in the format used by the sharable
    spreadsheet included with each Top 10 Pony Videos showcase ([example from
    February 2024][2]).

    [2]: https://docs.google.com/spreadsheets/d/1CCXeLR18mdDx6T2wQcxjTW-LRauTNFmG88OKvfSHy_M
    """

    records = []
    for url in urls:
        data = videos_data[url]

        if data is None:
            err(f"WARNING: Unable to generate sharable record for URL {url}; no data available. This video will not be represented in the output.")
            continue
        records.append(
            {
                'Rank': '',
                'Title': data['title'],
                'Link' : f'=VLOOKUP("{url}", IMPORTRANGE("{MASTER_ARCHIVE_URL}", "top10!D:I"), 6, FALSE)',
                'Votes': '',
                'Popularity': '',
                'Total voters': '',
                'Notes': '',
            }
        )

    return records


def generate_archive_csv(records: list[dict], filename: str):
    """Given a list of archive records, write them to a CSV file in a tabular
    format."""
    csv_path = Path(filename)

    header = ['year', 'month' , 'rank', 'link', 'title', 'channel', 'upload date', 'state', 'alternate link', 'found', 'notes']

    for record in records:
        if len(record) != len(header):
            raise Exception(f'Cannot generate archive CSV; header has {len(header)} values but {len(record)} record values were given')

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        csv_writer = csv.DictWriter(file, fieldnames=header)
        csv_writer.writeheader()
        csv_writer.writerows(records)


def generate_sharable_csv(records: list[dict], filename: str):
    """Given a list of sharable spreadsheet records, write them to a CSV file in
    a tabular format."""
    csv_path = Path(filename)
    header = ['Rank', 'Title', 'Link' , 'Votes', 'Popularity', 'Total voters', 'Notes']

    for record in records:
        if len(record) != len(header):
            raise Exception(f'Cannot generate sharable CSV; header has {len(header)} values but {len(record)} record values were given')

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        csv_writer = csv.DictWriter(file, fieldnames=header)
        csv_writer.writeheader()
        csv_writer.writerows(records)


def generate_showcase_description(urls: list[str], videos_data: dict[str, dict], silent: bool=False) -> str:
    """Given a list of URLs, generate the description for the showcase video
    ([example from February 2024][3]).

    [3]: https://www.youtube.com/watch?v=JOcVLEL-bgg
    """

    # Filter out any URLs for which no data is available, as we have no way to
    # handle those.
    urls_with_data = [url for url in urls if videos_data[url] is not None]
    urls_with_no_data = [url for url in urls if videos_data[url] is None]

    if len(urls_with_no_data) > 0:
        err(f'WARNING: No data available for the following {len(urls_with_no_data)} URLs: {", ".join(urls_with_no_data)}. These URLs will not be represented in the output.')

    urls = urls_with_data
    videos_data = {url: video_data for url, video_data in videos_data.items() if video_data is not None}

    # Guess the upload month and year based on most common
    upload_dates = [video['upload_date'] for video in videos_data.values()]
    upload_month_years = [date.strftime('%B %Y') for date in upload_dates]
    upload_month_year_freqs = get_freq_table(upload_month_years)
    upload_month_year_str = sorted(upload_month_year_freqs, key = lambda my: upload_month_year_freqs[my])[-1]

    if not silent:
        inf(f'Assuming showcase date of {upload_month_year_str} based on most common upload month and year.')

    # Calculate historical showcase dates
    upload_month_year_date = datetime.strptime(upload_month_year_str, '%B %Y')
    upload_year = upload_month_year_date.year
    last_year_date = upload_month_year_date.replace(year=upload_year - 1)
    five_years_ago_date = upload_month_year_date.replace(year=upload_year - 5)
    ten_years_ago_date = upload_month_year_date.replace(year=upload_year - 10)

    opening = "Be sure to check out the videos in the description below! The Top 10 Pony Videos is a long-running project to document and showcase the most popular My Little Pony videos in the brony community. Videos featured on the list are voted upon during a week-long voting process at the beginning of each month. This project has been active every single month since 2011!"

    project_links = {
        'Website': 'https://www.thetop10ponyvideos.com/',
        'Discord server': 'https://www.thetop10ponyvideos.com/discord',
    }

    sharable_links = {
        'YouTube playlist': '[ADD PLAYLIST LINK HERE]',
        'Spreadsheet': '[ADD SHARABLE SPREADSHEET LINK HERE]',
    }

    disclosures = 'Full disclosures: Any placement of tied videos was determined randomly by computer.'

    licensing = """
Top 10 Theme music: "Back Again (Original Mix)" by Archie
Get it here! https://mrarchie.bandcamp.com/track/back-again-original-mix
Used under Creative Commons license.
https://creativecommons.org/licenses/by-sa/3.0/"""

    mandatory_swearing = '[Mandatory swearing to help avoid being blacklisted as MFK: Fuck YouTube.]'

    desc = f'''{opening}


'''

    for link_text, url in project_links.items():
        desc += f'{link_text}:\n'
        desc += f'► {url}\n'


    desc += '''

► VIDEO LINKS:

'''

    for link_text, url in sharable_links.items():
        desc += f'• {link_text}: {url}\n'

    desc += '\n'

    # Note: URLs are listed in reverse order of popularity, as that's the way
    # they're presented in the video.
    for url in reversed(urls):
        video = videos_data[url]

        desc += f"""○ {video["title"]}
{url}
{video["uploader"]}

"""

    desc += """

► Honorable mentions:

○ 

○ 

○ 

○ 

"""


    desc += f"""

► The Top 10 Pony Videos of {last_year_date.strftime('%B %Y')}:

○ 

► The Top 10 Pony Videos of {five_years_ago_date.strftime('%B %Y')}:

○ 

► The Top 10 Pony Videos of {ten_years_ago_date.strftime('%B %Y')}:

○ 

"""

    desc += f"""


{disclosures}

"""

    desc += f"""{licensing}

"""

    desc += f"{mandatory_swearing}\n"

    return desc
