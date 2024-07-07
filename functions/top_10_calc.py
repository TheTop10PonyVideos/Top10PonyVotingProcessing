"""Functions for calculating video rankings based on number of votes."""

import csv
import requests
from datetime import datetime
from pathlib import Path
from functions.general import sample_item_without_replacement
from functions.messages import suc, inf, err

# Path to a local copy of the master Top 10 Pony Videos List (in CSV format).
local_top_10_archive_csv_path = 'data/top_10_master_archive.csv'

# URL to the downloadable CSV export of the master Top 10 Pony Videos List.
top_10_archive_csv_url = 'https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/export?format=csv'


def analyze_and_write_titles_to_csv(input_file: str, output_file: str):
    """Given an input CSV file containing rows of ballot data, count up the
    number of occurrences of each video voted for, and write a CSV containing
    the results sorted by number of votes.

    The input CSV should be a processed votes CSV with a layout similar to the
    following:

    Timestamp,,,,,,,,,,,,,,,,,,,,,
    4/1/2024 0:11:59,,Title A,,Title B, ... ,Title J,
    4/2/2024 0:11:59,,Title K,,Title L, ... ,Title T,
    ...

    """
    # TODO: Separate the CSV file operations and processing logic
    total_rows = 0
    title_counts = {}
    title_urls = {}

    for titles_row, urls_row in zip(titles_reader, urls_reader):
        # Check if any non-empty cell exists in the row
        if any(
            cell.strip() for cell in titles_row[1:]
        ):  # Skip the first column
            total_rows += 1

        titles_row = titles_row[
            2::2
        ]  # Skip the first column and odd-indexed columns
        urls_row = urls_row[
            2::2
        ]  # Skip the first column and odd-indexed columns

        for title, url in zip(titles_row, urls_row):
            title = title.strip()
            url = url.strip()
            if title:
                title_counts[title] = title_counts.get(title, 0) + 1
                title_urls[title] = url

    title_percentage = {  # calculates percentage
        title: (count / total_rows) * 100 for title, count in title_counts.items()
    }

    sorted_titles = sorted(  # sort counts based on percentage
        title_percentage.items(),
        key=lambda x: x[1],
        reverse=True,
    )  # Sorts titles by percentage

    with open(
        output_file, "w", newline="", encoding="utf-8"
    ) as csvfile:  # writes rows to the output
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Title", "Percentage", "Total Votes", "URL"])

        for title, percentage in sorted_titles:
            total_votes = title_counts[title]
            url = title_urls.get(title, "")
            csvwriter.writerow([title, f"{percentage:.4f}%", total_votes, url])


def process_shifted_voting_data(rows: list[list[str]]) -> list[list[str]]:
    """Given a set of data obtained from a "shifted" CSV (ie. a votes CSV with
    annotation columns inserted after every original column), return a list of
    rows containing just the data fields, with the "shifted" cells removed."""
    # Remove the header row
    data_rows = rows[1:]

    # Ignore the first column and odd-indexed columns
    data_rows = [row[2::2] for row in data_rows]

    return data_rows


def get_titles_to_urls_mapping(title_rows: list[list[str]], url_rows: list[list[str]]) -> dict[str, str]:
    """Given a set of (unshifted) title rows and a matching set of URL rows,
    return a dictionary that maps each title to its corresponding URL."""
    titles_to_urls = {}

    for title_row, url_row in zip(title_rows, url_rows, strict=True):
        for title, url in zip(title_row, url_row):
            titles_to_urls[title] = url

    return titles_to_urls

def calc_ranked_records(title_rows: list[list[str]], titles_to_urls: dict[str, str]) -> list[dict]:
    """Given a list of title rows, where each row represents the titles voted on
    in one ballot, calculate the frequency of occurrence of each title and
    generate a set of data records for the top 10 spreadsheet, ranked by
    percentage."""
    title_counts = {}
    for title_row in title_rows:
        for title in title_row:
            if title not in title_counts:
                title_counts[title] = 0
            title_counts[title] += 1

    title_percentages = {title: (count / len(title_rows)) * 100 for title, count in title_counts.items()}

    sorted_titles = sorted(title_percentages, key=lambda t: title_percentages[t], reverse=True)

    # If any titles have the same percentage of votes, then they are tied, and
    # we need to break such ties in order to produce a ranked top 10. To do this
    # we group each title by its percentage, then build a ranked top 10 by
    # randomly sampling each group, highest percentage first.
    percentage_groups = {}
    for title, percentage in title_percentages.items():
        if percentage not in percentage_groups:
            percentage_groups[percentage] = []
        percentage_groups[percentage].append(title)
    
    sorted_percentages = sorted(percentage_groups, reverse=True)

    ranked_titles = []
    tie_broken = {}

    for percentage in sorted_percentages:
        percentage_group = percentage_groups[percentage]
        tie_break_needed = len(percentage_group) > 1
        while len(percentage_group) > 0:
            sampled_title = sample_item_without_replacement(percentage_group)
            ranked_titles.append(sampled_title)
            tie_broken[sampled_title] = False
            if tie_break_needed:
                tie_broken[sampled_title] = True

    records = []
    for title in ranked_titles:
        record = {
            'Title': title,
            'Percentage': f'{title_percentages[title]:.4f}%',
            'Total Votes': title_counts[title],
            'URL': titles_to_urls[title],
            'Notes': 'Tie broken by random choice' if tie_broken[title] else ''
        }

        records.append(record)

    return records


def load_top_10_master_archive() -> list[dict]:
    """Load a local copy of the Top 10 Pony Videos List spreadsheet; or, if
    there's no local copy on the filesystem, export one from Google Sheets and
    save it first.

    The archive is returned as a list of records, with the key names being the
    field headers of the master archive file."""

    header = None    
    archive_records = None
    while True:
        try:
            # Try to load the local copy of the master archive spreadsheet
            with Path(local_top_10_archive_csv_path).open('r', encoding="utf-8") as file:
                inf('Loading local copy of master Top 10 Pony Videos archive...')
                reader = csv.DictReader(file)
                archive_records = [record for record in reader]
                header = reader.fieldnames
                break
        except FileNotFoundError:
            inf('No local copy of the master Top 10 Pony Videos archive exists, downloading one...')
            response = requests.get(top_10_archive_csv_url)
            Path(local_top_10_archive_csv_path).write_text(response.text)
            suc(f'Local copy of master Top 10 Pony Videos archive saved to {local_top_10_archive_csv_path}.')

    return archive_records


def get_history(archive_records: list[dict], from_date: datetime, anniversaries: list[int]) -> dict[int, dict]:
    """Given a set of archive records (in the format specified by the header of
    the Top 10 Pony Videos master archive), return all records which occurred on
    a given anniversary from the given date. For example, if the from date is
    April 2024 and the anniversaries are 1, 5, and 10 years, the selected
    records should be from April 2023, April 2019, and April 2013."""
    
    month, year = from_date.month, from_date.year

    # Index the archive records by month-year.
    month_year_records = {}
    for archive_record in archive_records:
        month_year = (int(archive_record['month']), int(archive_record['year']))
        if month_year not in month_year_records:
            month_year_records[month_year] = []
        month_year_records[month_year].append(archive_record)

    history_records = {}
    for num_years in anniversaries:
        anni_year = year - num_years
        try:
            # For each anniversary, get the entries for the archive for that
            # month and year.
            history_records[num_years] = month_year_records[(month, anni_year)]
        except KeyError:
            anni_date = datetime(anni_year, month, 1)
            anni_month_year_str = anni_date.strftime("%B %Y")
            err(f'Warning: No historical entries found for {anni_month_year_str}. Your local copy of the Top 10 Pony Videos master archive ({local_top_10_archive_csv_path}) may be out of date.')

    return history_records
