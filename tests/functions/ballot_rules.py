from unittest import TestCase
from functions.ballot_rules import (
    check_duplicates,
    check_fuzzy,
    check_ballot_uploader_occurrences,
)
from classes.voting import Ballot, Vote, Video
import pandas as pd


class TestFunctionsBallotRules(TestCase):
    def test_check_duplicates(self):
        ballots = [
            # No duplicates
            Ballot(
                "4/1/2024 9:00:00",
                [
                    Vote("https://example.com/1"),
                    Vote("https://example.com/2"),
                    Vote("https://example.com/3"),
                    Vote("https://example.com/4"),
                    Vote("https://example.com/5"),
                ],
            ),
            # One duplicate
            Ballot(
                "4/2/2024 9:00:00",
                [
                    Vote("https://example.com/1"),
                    Vote("https://example.com/2"),
                    Vote("https://example.com/1"),
                    Vote("https://example.com/3"),
                    Vote("https://example.com/4"),
                ],
            ),
            # 3 duplicates
            Ballot(
                "4/3/2024 9:00:00",
                [
                    Vote("https://example.com/1"),
                    Vote("https://example.com/2"),
                    Vote("https://example.com/1"),
                    Vote("https://example.com/1"),
                    Vote("https://example.com/2"),
                ],
            ),
        ]

        check_duplicates(ballots)

        self.assertTrue(ballots[0].votes[0].annotations.has_none())
        self.assertTrue(ballots[0].votes[1].annotations.has_none())
        self.assertTrue(ballots[0].votes[2].annotations.has_none())
        self.assertTrue(ballots[0].votes[3].annotations.has_none())
        self.assertTrue(ballots[0].votes[4].annotations.has_none())

        self.assertTrue(ballots[1].votes[0].annotations.has_none())
        self.assertTrue(ballots[1].votes[1].annotations.has_none())
        self.assertTrue(ballots[1].votes[2].annotations.has("DUPLICATE VIDEO"))
        self.assertTrue(ballots[1].votes[3].annotations.has_none())
        self.assertTrue(ballots[1].votes[4].annotations.has_none())

        self.assertTrue(ballots[2].votes[0].annotations.has_none())
        self.assertTrue(ballots[2].votes[1].annotations.has_none())
        self.assertTrue(ballots[2].votes[2].annotations.has("DUPLICATE VIDEO"))
        self.assertTrue(ballots[2].votes[3].annotations.has("DUPLICATE VIDEO"))
        self.assertTrue(ballots[2].votes[3].annotations.has("DUPLICATE VIDEO"))

    def test_check_fuzzy(self):
        ballots = [
            Ballot(
                "4/1/2024 9:00:00",
                [
                    Vote("https://example.com/1"),
                    Vote("https://example.com/2"),
                    Vote("https://example.com/3"),
                    Vote("https://example.com/4"),
                    Vote("https://example.com/5"),
                ],
            ),
            Ballot(
                "4/2/2024 9:00:00",
                [
                    Vote("https://example.com/6"),
                    Vote("https://example.com/7"),
                    Vote("https://example.com/8"),
                    Vote("https://example.com/9"),
                    Vote("https://example.com/10"),
                ],
            ),
            Ballot(
                "4/3/2024 9:00:00",
                [
                    Vote("https://example.com/11"),
                    Vote("https://example.com/12"),
                    Vote("https://example.com/13"),
                    Vote("https://example.com/14"),
                    Vote("https://example.com/15"),
                ],
            ),
        ]

        videos = pd.DataFrame([
            ["https://example.com/1", "AAAAA", "AAAAA", 60],
            ["https://example.com/2", "BBBBB", "BBBBB", 120],
            ["https://example.com/3", "BBBBB", "CCCCC", 180],
            ["https://example.com/4", "CCCCC", "DDDDD", 240],
            ["https://example.com/5", "DDDDD", "DDDDD", 300],
            ["https://example.com/6", "AAAAA", "AAAAA", 60],
            ["https://example.com/7","BBBBB", "BBBBB", 120],
            ["https://example.com/8", "CCCCC", "CCCCC", 180],
            ["https://example.com/9", "DDDDD", "DDDDD", 240],
            ["https://example.com/10", "EEEEE", "EEEEE", 300],
            ["https://example.com/11", "AAAAA", "AAAAA", 60],
            ["https://example.com/12", "AAAAA", "AAAAA", 60],
            ["https://example.com/13", "AAAAA", "AAAAA", 60],
            ["https://example.com/14", "AAAAA", "AAAAA", 60],
            ["https://example.com/15", "AAAAA", "AAAAA", 60],
        ], columns=['link', 'title', 'uploader', 'duration']).set_index('link')

        check_fuzzy(ballots, videos, 100)

        self.assertTrue(ballots[0].votes[0].annotations.has_none())
        self.assertEqual(1, ballots[0].votes[1].annotations.count())
        self.assertEqual(1, ballots[0].votes[2].annotations.count())
        self.assertEqual(1, ballots[0].votes[3].annotations.count())
        self.assertEqual(1, ballots[0].votes[4].annotations.count())
        self.assertTrue(
            ballots[0].votes[1].annotations.has("SIMILARITY DETECTED IN TITLE")
        )
        self.assertTrue(
            ballots[0].votes[2].annotations.has("SIMILARITY DETECTED IN TITLE")
        )
        self.assertTrue(
            ballots[0].votes[3].annotations.has("SIMILARITY DETECTED IN UPLOADER")
        )
        self.assertTrue(
            ballots[0].votes[4].annotations.has("SIMILARITY DETECTED IN UPLOADER")
        )

        self.assertTrue(ballots[1].votes[0].annotations.has_none())
        self.assertTrue(ballots[1].votes[1].annotations.has_none())
        self.assertTrue(ballots[1].votes[2].annotations.has_none())
        self.assertTrue(ballots[1].votes[3].annotations.has_none())
        self.assertTrue(ballots[1].votes[4].annotations.has_none())

        self.assertEqual(1, ballots[2].votes[0].annotations.count())
        self.assertEqual(1, ballots[2].votes[1].annotations.count())
        self.assertEqual(1, ballots[2].votes[2].annotations.count())
        self.assertEqual(1, ballots[2].votes[3].annotations.count())
        self.assertEqual(1, ballots[2].votes[4].annotations.count())
        self.assertTrue(
            ballots[2]
            .votes[0]
            .annotations.has("SIMILARITY DETECTED IN TITLE AND UPLOADER AND DURATION")
        )
        self.assertTrue(
            ballots[2]
            .votes[1]
            .annotations.has("SIMILARITY DETECTED IN TITLE AND UPLOADER AND DURATION")
        )
        self.assertTrue(
            ballots[2]
            .votes[2]
            .annotations.has("SIMILARITY DETECTED IN TITLE AND UPLOADER AND DURATION")
        )
        self.assertTrue(
            ballots[2]
            .votes[3]
            .annotations.has("SIMILARITY DETECTED IN TITLE AND UPLOADER AND DURATION")
        )
        self.assertTrue(
            ballots[2]
            .votes[4]
            .annotations.has("SIMILARITY DETECTED IN TITLE AND UPLOADER AND DURATION")
        )

    def test_check_ballot_uploader_occurrences(self):
        ballots = [
            # Too many votes for one creator
            Ballot(
                "4/1/2024 9:00:00",
                [
                    Vote("https://example.com/1"),
                    Vote("https://example.com/2"),
                    Vote("https://example.com/3"),
                    Vote("https://example.com/4"),
                    Vote("https://example.com/5"),
                    Vote("https://example.com/6"),
                    Vote("https://example.com/7"),
                    Vote("https://example.com/8"),
                    Vote("https://example.com/9"),
                    Vote("https://example.com/10"),
                ],
            ),
            # Acceptable
            Ballot(
                "4/2/2024 9:00:00",
                [
                    Vote("https://example.com/11"),
                    Vote("https://example.com/12"),
                    Vote("https://example.com/13"),
                    Vote("https://example.com/14"),
                    Vote("https://example.com/15"),
                ],
            ),
        ]

        videos = pd.DataFrame([
            ["https://example.com/1", "AAAAA"],
            ["https://example.com/2", "AAAAA"],
            ["https://example.com/3", "AAAAA"],
            ["https://example.com/4", "AAAAA"],
            ["https://example.com/5", "BBBBB"],
            ["https://example.com/6", "BBBBB"],
            ["https://example.com/7", "BBBBB"],
            ["https://example.com/8", "CCCCC"],
            ["https://example.com/9", "CCCCC"],
            ["https://example.com/10", "DDDDD"],
            ["https://example.com/11", "AAAAA"],
            ["https://example.com/12", "AAAAA"],
            ["https://example.com/13", "BBBBB"],
            ["https://example.com/14", "BBBBB"],
            ["https://example.com/15", "CCCCC"]
        ], columns=['link', 'uploader']).set_index('link')

        check_ballot_uploader_occurrences(ballots, videos)
        self.assertTrue(ballots[0].votes[0].annotations.has("DUPLICATE CREATOR"))
        self.assertTrue(ballots[0].votes[1].annotations.has("DUPLICATE CREATOR"))
        self.assertTrue(ballots[0].votes[2].annotations.has("DUPLICATE CREATOR"))
        self.assertTrue(ballots[0].votes[3].annotations.has("DUPLICATE CREATOR"))
        self.assertTrue(ballots[0].votes[4].annotations.has("DUPLICATE CREATOR"))
        self.assertTrue(ballots[0].votes[5].annotations.has("DUPLICATE CREATOR"))
        self.assertTrue(ballots[0].votes[6].annotations.has("DUPLICATE CREATOR"))
        self.assertTrue(ballots[0].votes[7].annotations.has_none())
        self.assertTrue(ballots[0].votes[8].annotations.has_none())
        self.assertTrue(ballots[0].votes[9].annotations.has_none())
        self.assertTrue(ballots[1].votes[0].annotations.has_none())
        self.assertTrue(ballots[1].votes[1].annotations.has_none())
        self.assertTrue(ballots[1].votes[2].annotations.has_none())
        self.assertTrue(ballots[1].votes[3].annotations.has_none())
        self.assertTrue(ballots[1].votes[4].annotations.has_none())

    def test_check_ballot_uploader_diversity(self):
        # TODO: should this be removed completely, or should
        # the uploader diversity be kept an optional check that's
        # toggled off by default?
        ballots = [
            # All votes for the same uploader
            Ballot(
                "4/1/2024 9:00:00",
                [
                    Vote("https://example.com/1"),
                    Vote("https://example.com/2"),
                    Vote("https://example.com/3"),
                    Vote("https://example.com/4"),
                    Vote("https://example.com/5"),
                    Vote("https://example.com/6"),
                    Vote("https://example.com/7"),
                    Vote("https://example.com/8"),
                    Vote("https://example.com/9"),
                    Vote("https://example.com/10"),
                ],
            ),
            # Sufficiently diverse
            Ballot(
                "4/2/2024 9:00:00",
                [
                    Vote("https://example.com/11"),
                    Vote("https://example.com/12"),
                    Vote("https://example.com/13"),
                    Vote("https://example.com/14"),
                    Vote("https://example.com/15"),
                ],
            ),
        ]

        videos = {
            "https://example.com/1": Video({"uploader": "AAAAA"}),
            "https://example.com/2": Video({"uploader": "AAAAA"}),
            "https://example.com/3": Video({"uploader": "AAAAA"}),
            "https://example.com/4": Video({"uploader": "AAAAA"}),
            "https://example.com/5": Video({"uploader": "AAAAA"}),
            "https://example.com/6": Video({"uploader": "AAAAA"}),
            "https://example.com/7": Video({"uploader": "AAAAA"}),
            "https://example.com/8": Video({"uploader": "AAAAA"}),
            "https://example.com/9": Video({"uploader": "AAAAA"}),
            "https://example.com/10": Video({"uploader": "AAAAA"}),
            "https://example.com/11": Video({"uploader": "AAAAA"}),
            "https://example.com/12": Video({"uploader": "BBBBB"}),
            "https://example.com/13": Video({"uploader": "CCCCC"}),
            "https://example.com/14": Video({"uploader": "DDDDD"}),
            "https://example.com/15": Video({"uploader": "EEEEE"}),
        }

        self.assertTrue(ballots[1].votes[0].annotations.has_none())
        self.assertTrue(ballots[1].votes[1].annotations.has_none())
        self.assertTrue(ballots[1].votes[2].annotations.has_none())
        self.assertTrue(ballots[1].votes[3].annotations.has_none())
        self.assertTrue(ballots[1].votes[4].annotations.has_none())
