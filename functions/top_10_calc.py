"""Functions for calculating video rankings based on number of votes."""

from datetime import datetime
from classes.typing import ArchiveRecord
from functions.general import sample_item_without_replacement
from functions.messages import err
from data.globals import local_top_10_archive_csv_path
import pandas as pd


def process_shifted_voting_data(df: pd.DataFrame):
    """Given a set of data obtained from a "shifted" CSV (ie. a votes CSV with
    annotation columns inserted after every original column), return a list of
    rows containing just the data fields, with the "shifted" cells removed."""
    # Ignore the first column and odd-indexed columns
    return df.iloc[:, 2::2]


def get_titles_to_urls_mapping(
    titles_df: pd.DataFrame, urls_df: pd.DataFrame
) -> dict[str, str]:
    """Given an (unshifted) titles df and a matching one of URLs,
    return a dictionary that maps each title to its corresponding URL.

    If the same title maps to multiple URLs, the last-encountered title-to-URL
    mapping will be used."""
    titles_to_urls = {}

    for title, url in zip(titles_df.stack(), urls_df.stack(), strict=True):
        titles_to_urls[title] = url

    return titles_to_urls


def get_titles_to_uploaders(
    titles_to_urls: dict[str, str], videos_data: dict[str, dict]
) -> dict[str, str]:
    """Given a dictionary mapping titles to urls, look up the
    return a dictionary that maps each title to its corresponding URL."""

    titles_to_uploaders = {}

    for title, url in titles_to_urls.items():
        video_data = videos_data[url]
        titles_to_uploaders[title] = (
            video_data["uploader"] if video_data is not None else None
        )

    return titles_to_uploaders


def create_top10_csv_data(
    title_rows: pd.DataFrame,
    titles_to_urls: dict[str, str],
    titles_to_uploaders: dict[str, str],
    scoring_func,
    upload_date: datetime,
    anniversaries: list[int],
    archive_records: list[ArchiveRecord]
) -> list[dict]:
    """Given a list of title rows, use a scoring function to calculate
    rankings for all titles, and generate the CSV data for a Top 10 CSV file.
    The resulting file includes the top 10 videos from those provided, an
    Honorable Mentions list containing all videos that didn't make the top 10,
    and a History section which sources old videos published on anniversaries of
    the current showcase month.

    Mappings for URLs and uploaders must be supplied to populate the URL and
    Uploader columns.

    For the History section, the upload date, desired year-anniversaries, and a
    list of master archive records must also be supplied."""

    # Calculate a ranked list of videos, highest ranked first, with tie-breaks
    # resolved automatically by random choice.
    ranked_records = calc_ranked_records(
        title_rows, titles_to_urls, titles_to_uploaders, scoring_func
    )

    if len(ranked_records) < 10:
        raise Exception(
            f"Cannot create data for calculated Top 10 spreadsheet; there are only {len(ranked_records)} entries"
        )

    # Separate the top 10 videos from the rest.
    top_10_records = ranked_records[:10]
    non_top_10_records = ranked_records[10:]

    # For the non-top 10 videos, we don't care about tie breaks, so remove the
    # Notes for those entries.
    for record in non_top_10_records:
        record["Notes"] = ""

    # If any of the non-top 10 videos would have made it into the top 10 but
    # were excluded due to a tie break, add a special note for them.
    tenth_place_record = top_10_records[9]
    for record in non_top_10_records:
        if record["Total Votes"] == tenth_place_record["Total Votes"]:
            record["Notes"] = "Missed out on top 10 due to tie break"
        else:
            break

    # Create some heading rows and blank rows.
    honorable_mentions_heading = {"Title": "HONORABLE MENTIONS"}
    history_heading = {"Title": "HISTORY"}
    blank_row = {"Title": ""}

    # Read the Top 10 Pony Videos master archive and extract records for the 1
    # year, 5 year, and 10 year anniversaries of the upload date.
    history = get_history(archive_records, upload_date, anniversaries)

    # Create history records for each of the anniversaries.
    s = lambda n: "" if n == 1 else "s"
    anni_headings = {y: {"Title": f"{y} year{s(y)} ago"} for y in anniversaries}
    anni_records = {}
    for years_ago in anniversaries:
        records = history.get(years_ago, [])

        # Sort the archive records by rank, so that they match the ordering in
        # the calculated top 10 spreadsheet.
        records = sorted(records, key=lambda r: r["rank"])
        anni_records[years_ago] = []
        for record in records:
            link = record["link"]
            alt_link = record["alternate_link"]
            anni_record = {
                "Title": record["title"],
                "Uploader": record["channel"],
                "URL": link,
            }

            if alt_link != link:
                anni_record["Notes"] = f'Alt link: {record["alternate_link"]}'

            anni_records[years_ago].append(anni_record)

    # Assemble all the rows together.
    output_records = []
    output_records += top_10_records
    output_records.append(blank_row)
    output_records.append(honorable_mentions_heading)
    output_records.append(blank_row)
    output_records += non_top_10_records
    output_records.append(blank_row)
    output_records.append(history_heading)
    output_records.append(blank_row)
    for years_ago in anniversaries:
        output_records.append(anni_headings[years_ago])
        output_records.append(blank_row)
        for anni_record in anni_records[years_ago]:
            output_records.append(anni_record)
        output_records.append(blank_row)

    return output_records


def calc_ranked_records(
    titles_df: pd.DataFrame,
    titles_to_urls: dict[str, str],
    titles_to_uploaders: dict[str, str],
    scoring_func,
    min_votes = 1
) -> list[dict]:
    """Given a dataframe of title rows, where each row represents the titles voted on
    in one ballot, calculate the frequency of occurrence of each title and
    generate a set of data records for the top 10 spreadsheet.

    A scoring function must be supplied which accepts the title rows as input,
    and returns a score for each title, plus the total possible score. These
    scores are used to determine the ranking of each record."""

    # Ensure each (non-blank) title row has at least the minimum allowed number of titles.
    title_row_checks = check_blank_titles(titles_df)
    violators = titles_df
    for i, checked_row in enumerate(title_row_checks):
        num_non_blank, num_blank = checked_row
        if num_non_blank == 0:
            continue
        if num_non_blank < min_votes:
            # The ballot line is reported as 2 indices after the row index, since
            # most editors start row indices at 1, and there's a header row that
            # needs to be skipped.
            ballot_line = i + 2
            raise ValueError(
                f"Error when calculating rankings; at least {min_votes} votes are required in each ballot, but ballot line {ballot_line} has only {num_non_blank}"
            )

    scores, total_score = scoring_func(titles_df)

    title_percentages = {
        title: (score / total_score) * 100 for title, score in scores.items()
    }

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

    # Create the list of records, ordered by ranking.
    records = []
    for title in ranked_titles:
        uploader = titles_to_uploaders[title]
        record = {
            "Title": title,
            "Uploader": uploader if uploader is not None else "",
            "Percentage": f"{title_percentages[title]:.4f}%",
            "Total Votes": scores[title],
            "URL": titles_to_urls[title],
            "Notes": "Tie broken randomly by computer" if tie_broken[title] else "",
        }

        records.append(record)

    return records


def check_blank_titles(titles_df: pd.DataFrame):
    """Check a dataframe of titles and return a 2-tuple (n, b) for each row, where n is the number of non-blank titles and b is the number of blank titles."""
    result = titles_df.apply(
        lambda row: ((row.str.strip() != '').sum(), (row.str.strip() == '').sum()), axis=1
    ) borked

    return result.to_list()


def score_by_total_votes(title_rows: pd.DataFrame):
    """Given a list of title rows, return a dictionary mapping each title to the
    number of times it occurs in all rows. Blank titles are ignored.

    For example, if the title "Example" appears in 6 of the given rows, then
    "Example" will receive a score of 6.

    The total number of eligible ballots (ie. non-blank ballots) is also
    returned, which allows scores to be expressed as a percentage of the total
    number of ballots."""
    # Titles as a dataframe with a column for vote titles, and another column for which ballot the vote belongs to.
    title_rows = title_rows.copy()
    title_rows['ballot id'] = title_rows.index
    ballot_votes_long = title_rows.melt(id_vars='ballot id', value_name='title', ignore_index=False).dropna()

    individual_scores = ballot_votes_long.groupby('title').size()
    total_ballots = ballot_votes_long.groupby('ballot id').ngroups

    return individual_scores, total_ballots


def score_weight_by_ballot_size(title_rows: pd.DataFrame):
    """Given a list of title rows, return a dictionary mapping each title to a
    score. The score is calculated as follows:

    * The ballot with the most votes (usually 10) is defined to be a "full"
      ballot.
    * Each ballot is given a weighting between 0 and 1, which is calculated as:

          number of votes / full ballot size

      For example, if the full ballot size is 10, a ballot with 6 votes has a
      weighting of 6 / 10 = 0.6.
    * The votes for each title are counted up, but each vote is weighted
      according to the ballot's weighting.

    Blank titles are ignored.

    The theoretical maximum score is also returned, to allow scores to be
    expressed as a percentage."""
    title_rows = title_rows.copy()
    title_rows['ballot id'] = title_rows.index
    ballot_votes_long = title_rows.melt(id_vars='ballot id', value_name='title', ignore_index=False).dropna()

    full_ballot_size = ballot_votes_long.groupby('ballot id')['title'].count().max()
    ballot_votes_long['weight'] = ballot_votes_long.groupby('ballot id')['title'].transform('count') / full_ballot_size

    individual_scores = ballot_votes_long.groupby('title')['weight'].sum()
    max_total_score = ballot_votes_long.groupby('ballot id')['weight'].first().sum()

    return individual_scores, max_total_score


def score_half_weight_by_ballot_size(
    title_rows: pd.DataFrame,
) -> tuple[dict[str, int], float]:
    """Given a list of title rows, return a dictionary mapping each title to a
    score. The score is calculated as follows:

    * Each ballot is given a weighting between 0 and 1. If the ballot contains
      5 or more titles, the weighting is 1. Otherwise, it is n/5, where n is
      the number of titles in the ballot.

      For example, if the ballot contains 7 titles, it has a weighting of 1.
      If the ballot contains 3 titles, it has a weighting of 3 / 5 = 0.6.
    * The votes for each title are counted up, and each vote is weighted
      according to the ballot's weighting.

    The theoretical maximum score is also returned, to allow scores to be
    expressed as a percentage."""
    title_rows = title_rows.copy()
    title_rows['ballot id'] = title_rows.index
    ballot_votes_long = title_rows.melt(id_vars='ballot id', value_name='title', ignore_index=False).dropna()

    ballot_votes_long['weight'] = (ballot_votes_long.groupby('ballot id')['title'].transform('count') / 5).clip(upper=1)

    individual_scores = ballot_votes_long.groupby('title')['weight'].sum()
    max_total_score = ballot_votes_long.groupby('ballot id')['weight'].first().sum()

    return individual_scores, max_total_score


def get_history(
    archive_records: list[ArchiveRecord],
    from_date: datetime,
    anniversaries: list[int]
) -> dict[int, dict]:
    """Given a set of archive records (in the format specified by the header of
    the Top 10 Pony Videos master archive), return all records which occurred on
    a given anniversary from the given date. For example, if the from date is
    April 2024 and the anniversaries are 1, 5, and 10 years, the selected
    records should be from April 2023, April 2019, and April 2013."""

    month, year = from_date.month, from_date.year

    # Index the archive records by month-year.
    month_year_records = {}
    for archive_record in archive_records:
        month_year = (int(archive_record["month"]), int(archive_record["year"]))
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
            err(
                f"Warning: No historical entries found for {anni_month_year_str}. Your local copy of the Top 10 Pony Videos master archive ({local_top_10_archive_csv_path}) may be out of date, or you may be running a calculation on old voting data."
            )

    return history_records
