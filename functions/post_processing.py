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


def create_post_processed_records(calc_records: list[dict], videos_data: dict[str, dict], silent: bool=False) -> list[str]:
    """Given a "calc record" (a record obtained from the output of the calc
    script) and a dictionary mapping each video URL to its data, return a
    "post-processed record", which contains all of the information needed for
    post-processing operations."""

    # Sort the vote counts and assign a rank to each.
    vote_counts = set([int(record['Total Votes']) for record in calc_records])
    sorted_vote_counts = sorted(vote_counts, reverse=True)
    ranked_vote_counts = {vote_count:i+1 for i, vote_count in enumerate(sorted_vote_counts)}

    post_proc_records = []
    for calc_record in calc_records:
        url = calc_record['URL']
        video_data = None
        if url in videos_data:
            video_data = videos_data[url]
        else:
            if not silent:
                err(f'WARNING: No video data available for URL {url}.')

        # Probably shouldn't do this, but since one of the fields requested by
        # the sharable spreadsheet is the total number of voters, we can
        # actually reverse-engineer that figure from votes and percentage:
        percentage = float(calc_record['Percentage'].strip('%'))
        votes = int(calc_record['Total Votes'])
        total_voters = round((100 * votes) / percentage)

        post_proc_record = {
            'url': url,
            'title': calc_record['Title'],
            'uploader': None,
            'upload_date': None,
            'rank': ranked_vote_counts[votes],
            'votes': votes,
            'percentage': percentage,
            'total_voters': total_voters,
        }

        # If video data is available, use that to supply some of the field data.
        if video_data is not None:
            post_proc_record['title'] = video_data['title']
            post_proc_record['uploader'] = video_data['uploader']
            post_proc_record['upload_date'] = video_data['upload_date']

        post_proc_records.append(post_proc_record)

    return post_proc_records


def generate_archive_records(post_proc_records: list[dict]) -> list[dict]:
    """Given a list of post-processed records, generate a list of data records
    in the format used by [Flynn's Top 10 Pony Videos List][1].

    [1]: https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E
    """

    records = []
    # Note: records created in reverse order as per the convention used in the
    # master archive spreadsheet.
    for post_proc_record in reversed(post_proc_records):
        record = {
            'year': post_proc_record['upload_date'].year if post_proc_record['upload_date'] is not None else '',
            'month': post_proc_record['upload_date'].month if post_proc_record['upload_date'] is not None else '',
            'rank': post_proc_record['rank'],
            'link': post_proc_record['url'],
            'title': post_proc_record['title'],
            'channel': post_proc_record['uploader'] if post_proc_record['uploader'] is not None else '',
            'upload date': post_proc_record['upload_date'].strftime('%Y-%m-%d') if post_proc_record['upload_date'] is not None else '',
            'state': '',
            'alternate link': post_proc_record['url'],
            'found': '',
            'notes': '',
        }
    
        records.append(record)

    return records

def generate_sharable_records(post_proc_records: list[dict]) -> list[dict]:
    """Given a list of post-processed records, generate a list of data records
    in the format used by the sharable spreadsheet included with each Top 10
    Pony Videos showcase ([example from February 2024][2]).

    [2]: https://docs.google.com/spreadsheets/d/1CCXeLR18mdDx6T2wQcxjTW-LRauTNFmG88OKvfSHy_M
    """

    records = []
    for post_proc_record in post_proc_records:
        record = {
            'Rank': post_proc_record['rank'],
            'Title': post_proc_record['title'],
            'Link' : f'=VLOOKUP("{post_proc_record["url"]}", IMPORTRANGE("{MASTER_ARCHIVE_URL}", "top10!D:I"), 6, FALSE)',
            'Votes': post_proc_record['votes'],
            'Popularity': f'{post_proc_record["percentage"]}%',
            'Total voters': post_proc_record['total_voters'],
            'Notes': '',
        }
    
        records.append(record)

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


def generate_showcase_description(post_proc_records: list[dict], silent: bool=False) -> str:
    """Given a list of URLs, generate the description for the showcase video
    ([example from February 2024][3]).

    [3]: https://www.youtube.com/watch?v=JOcVLEL-bgg
    """

    # Filter out any records for which we don't have sufficient data available,
    # as we have no way to handle those.
    insufficient_data = lambda r: r['upload_date'] is None or r['uploader'] is None
    records_with_insufficient_data = [record for record in post_proc_records if insufficient_data(record)]

    records_with_sufficient_data = [record for record in post_proc_records if not insufficient_data(record)]

    if len(records_with_insufficient_data) > 0:
        if not silent:
            urls_with_insufficient_data = [record['url'] for record in records_with_insufficient_data]
            err(f'WARNING: Insufficient data for the following {len(urls_with_insufficient_data)} URLs: {", ".join(urls_with_insufficient_data)}. These URLs will not be represented in the output.')

    post_proc_records = records_with_sufficient_data

    # Guess the upload month and year based on most common
    upload_dates = [record['upload_date'] for record in post_proc_records]
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
    for record in reversed(post_proc_records):
        desc += f"""○ {record["title"]}
{record["url"]}
{record["uploader"]}

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
