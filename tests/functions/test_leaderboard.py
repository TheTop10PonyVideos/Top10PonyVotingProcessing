import pytest
from functions.leaderboard import (
    calc_leaderboard,
    compare_leaderboards,
    get_year_months_with_vote_data
)

def test_calc_leaderboard():
    archive = [
        {"year": "2025", "month": "3", "channel": "Channel A", "voters": "20%"},
        {"year": "2025", "month": "3", "channel": "Channel B", "voters": "20%"},
        {"year": "2025", "month": "3", "channel": "Channel C", "voters": "30%"},
        {"year": "2025", "month": "2", "channel": "Channel A", "voters": "20%"},
        {"year": "2025", "month": "2", "channel": "Channel B", "voters": "20"},
        {"year": "2025", "month": "2", "channel": "Channel D", "voters": "30%"},
        {"year": "2025", "month": "1", "channel": "Channel A", "voters": "20%"},
        {"year": "2025", "month": "1", "channel": "Channel E", "voters": "10%"},
        {"year": "2025", "month": "1", "channel": "Channel F", "voters": "40%"},
        {"year": "2025", "month": "1", "channel": "Channel G", "voters": ""},
        {"year": "2025", "month": "1", "channel": "Channel E", "voters": ""},
    ]

    leaderboard = calc_leaderboard(archive, 3, 2025, 3)

    assert len(leaderboard) == 6
    assert "Channel A" in leaderboard
    assert "Channel B" in leaderboard
    assert "Channel C" in leaderboard
    assert "Channel D" in leaderboard
    assert "Channel E" in leaderboard
    assert "Channel F" in leaderboard
    assert "Channel G" not in leaderboard
    assert leaderboard["Channel A"] == 60
    assert leaderboard["Channel B"] == 40
    assert leaderboard["Channel C"] == 30
    assert leaderboard["Channel D"] == 30
    assert leaderboard["Channel E"] == 10
    assert leaderboard["Channel F"] == 40


def test_compare_leaderboards():
    board_a = {
        "Channel A": 5,
        "Channel B": 20,
        "Channel C": 30,
    }

    board_b = {
        "Channel B": 10,
        "Channel C": 50,
        "Channel D": 40,
    }

    diff = compare_leaderboards(board_a, board_b)
    assert len(diff) == 4
    assert "Channel A" in diff
    assert "Channel B" in diff
    assert "Channel C" in diff
    assert "Channel D" in diff

    assert diff["Channel A"]["old_vote_share"] == 5
    assert diff["Channel A"]["new_vote_share"] == 0
    assert diff["Channel A"]["vote_share_diff"] == -5
    assert diff["Channel A"]["old_rank"] == 3
    assert diff["Channel A"]["new_rank"] is None
    assert diff["Channel A"]["rank_diff"] is None

    assert diff["Channel B"]["old_vote_share"] == 20
    assert diff["Channel B"]["new_vote_share"] == 10
    assert diff["Channel B"]["vote_share_diff"] == -10
    assert diff["Channel B"]["old_rank"] == 2
    assert diff["Channel B"]["new_rank"] == 3
    assert diff["Channel B"]["rank_diff"] == -1

    assert diff["Channel C"]["old_vote_share"] == 30
    assert diff["Channel C"]["new_vote_share"] == 50
    assert diff["Channel C"]["vote_share_diff"] == 20
    assert diff["Channel C"]["old_rank"] == 1
    assert diff["Channel C"]["new_rank"] == 1
    assert diff["Channel C"]["rank_diff"] == 0

    assert diff["Channel D"]["old_vote_share"] == 0
    assert diff["Channel D"]["new_vote_share"] == 40
    assert diff["Channel D"]["vote_share_diff"] == 40
    assert diff["Channel D"]["old_rank"] is None
    assert diff["Channel D"]["new_rank"] == 2
    assert diff["Channel D"]["rank_diff"] is None


def test_get_year_months_with_vote_data():
    archive = [
        {"year": "2025", "month": "3", "channel": "Channel A", "voters": "20%"},
        {"year": "2025", "month": "1", "channel": "Channel B", "voters": "30%"},
        {"year": "2024", "month": "9", "channel": "Channel C", "voters": "40%"},
        {"year": "2024", "month": "9", "channel": "Channel D", "voters": ""},
        {"year": "2024", "month": "8", "channel": "Channel E", "voters": ""},
    ]

    year_months = get_year_months_with_vote_data(archive)
    assert len(year_months) == 3
    assert year_months[0] == (2025, 3)
    assert year_months[1] == (2025, 1)
    assert year_months[2] == (2024, 9)
