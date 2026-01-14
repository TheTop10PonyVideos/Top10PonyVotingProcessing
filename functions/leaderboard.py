"""Functions for handling leaderboards and leaderboard comparisons."""

def calc_leaderboard(
    archive: list[dict],
    month: int,
    year: int,
    period_months: int=12,
) -> dict[str, float]:
    """Given an object representing records from the master archive[1],
    calculate a leaderboard of which voters have the highest total vote share
    over the given time period.

    Example for a 3-month period:

        year   month   channel     voters
        2025   3       Creator A   20%
        2025   3       Creator B   20%
        2025   3       Creator C   30%
        2025   2       Creator A   20%
        2025   2       Creator B   20%
        2025   2       Creator D   30%
        2025   1       Creator A   20%
        2025   1       Creator E   10%
        2025   1       Creator F   40%

    In the above example, Creator A has the highest total vote share (60% when
    added up over the 3 months). The resulting leaderboard would look like this:

        creator     total vote share
        Creator A   60%
        Creator B   40%
        Creator F   40%
        Creator C   30%
        Creator D   30%
        Creator E   10%

    `month` and `year` specify the end date of the time period, and
    `period_months` specifies how many preceding months the vote share should be
    counted over. The leaderboard is returned as a dictionary mapping each
    channel (i.e. creator) to their total vote share over the given period.

    Note that the given month and year are included in the time period - for
    example, if month and year is 4 and 2025 (April 2025) and the period is 12
    months, the first month in that period is May 2024 and the last month is
    April 2025.

    [1]: https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E
    """

    # Make a list of all year-month values that need to be considered. For
    # example, if year = 2025, month = 2, and period_months = 3, the expected
    # year-month values are (2025, 2), (2025, 1), (2024, 12).
    year_months = []
    y = year
    m = month
    for i in range(period_months):
        year_months.append((y, m))
        m -= 1
        if m == 0:
            m = 12
            y -= 1

    # Index archive by year-month
    indexed_archive = {}
    for record in archive:
        year_month = (int(record["year"]), int(record["month"]))
        if year_month not in indexed_archive:
            indexed_archive[year_month] = []
        indexed_archive[year_month].append(record)

    channel_vote_shares = {}
    for y, m in year_months:
        # Get all records for this year-month. Ignore year-months for which
        # there is no data.
        records = None
        try:
            records = indexed_archive[(y, m)]
        except KeyError:
            continue

        for record in records:
            channel = record["channel"]
            vote_share = record["voters"]

            # Ignore missing vote shares
            if vote_share == "":
                continue
            if vote_share.endswith("%"):
                vote_share = vote_share[:-1]

            vote_share = float(vote_share)

            if channel not in channel_vote_shares:
                channel_vote_shares[channel] = 0

            channel_vote_shares[channel] += vote_share

    return channel_vote_shares


def compare_leaderboards(board_a: dict, board_b: dict) -> dict:
    """Given 2 leaderboards A and B, compare them and output, for each creator,
    an object representing the difference in their vote share and rankings from
    board A to board B.

    For example, if a creator has vote share 300 in board A and vote share 200
    in board B, their change in vote share will be -100.

    It's possible a given creator may appear in only one of the leaderboards but
    not both. If that's the case, no rank change will be recorded, but they will
    be assumed to have a vote share of 0 for whichever board they are not in.
    (e.g. If they are not on board A but have a vote share of 50 on board B,
    their change in vote share is 50)."""

    # Get a list of all creators in both leaderboards
    creators_a = set([c for c in board_a])
    creators_b = set([c for c in board_b])
    creators = [c for c in creators_a.union(creators_b)]

    # Sort the leaderboards by vote share to get creator rankings
    ranked_creators_a = sorted(board_a, key=lambda c: board_a[c], reverse=True)
    ranked_creators_b = sorted(board_b, key=lambda c: board_b[c], reverse=True)

    # Calculate difference in vote share and rank for all creators
    diff = {}
    for creator in creators:
        vote_share_a = 0
        vote_share_b = 0
        rank_a = None
        rank_b = None
        if creator in creators_a:
            vote_share_a = board_a[creator]
            rank_a = ranked_creators_a.index(creator) + 1
        if creator in creators_b:
            vote_share_b = board_b[creator]
            rank_b = ranked_creators_b.index(creator) + 1

        rank_diff = None
        if rank_a is not None and rank_b is not None:
            # Note that going down in rank means an increase in rank number
            rank_diff = rank_a - rank_b

        diff[creator] = {
            "old_vote_share": vote_share_a,
            "new_vote_share": vote_share_b,
            "vote_share_diff": vote_share_b - vote_share_a,
            "old_rank": rank_a,
            "new_rank": rank_b,
            "rank_diff": rank_diff,
        }

    return diff


def get_year_months_with_vote_data(archive: list[dict]) -> list[tuple[int, int]]:
    """Given an object representing records from the master archive, return a
    list of all year-months for which vote share data is available, sorted most
    recent first."""
    year_months_set = set()
    for record in archive:
        year_month = (int(record["year"]), int(record["month"]))

        if year_month in year_months_set:
            continue

        vote_share = record["voters"]
        if vote_share != "":
            year_months_set.add(year_month)
    
    year_months = [ym for ym in year_months_set]
    year_months = sorted(year_months, key=lambda ym: ym[1], reverse=True)
    year_months = sorted(year_months, key=lambda ym: ym[0], reverse=True)

    return year_months
