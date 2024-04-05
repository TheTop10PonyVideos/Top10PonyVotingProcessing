from unittest import TestCase
from datetime import datetime
from pytz import timezone
from functions.voting import (
    process_votes_csv,
    process_votes_csv_row,
    validate_video_data,
    generate_annotated_csv_data,
)
from classes.voting import Ballot, Vote, Video


class TestFunctionsVoting(TestCase):
    def test_process_votes_csv(self):
        tz = timezone("Etc/UTC")

        csv_rows = [
            ["Timestamp", "", "", "", "", "", "", "", "", ""],
            [
                "4/1/2024 9:00:00",
                "https://example.com/1",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "12/31/2024 23:59:59",
                "https://example.com/2",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "02/02/2022 02:02:02",
                "https://example.com/3",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "11/6/2023 10:23:36",
                "https://example.com/4",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
        ]

        ballots = process_votes_csv(csv_rows)
        self.assertEqual(4, len(ballots))
        self.assertEqual("2024-04-01T09:00:00", ballots[0].timestamp.isoformat())
        self.assertEqual("2024-12-31T23:59:59", ballots[1].timestamp.isoformat())
        self.assertEqual("2022-02-02T02:02:02", ballots[2].timestamp.isoformat())
        self.assertEqual("2023-11-06T10:23:36", ballots[3].timestamp.isoformat())

        invalid_csv_rows = [
            ["Invalid", "", "", "", "", "", "", "", "", "", ""],
            ["Invalid", "", "", "", "", "", "", "", "", "", ""],
            ["Invalid", "", "", "", "", "", "", "", "", "", ""],
        ]

        with self.assertRaises(ValueError):
            ballots = process_votes_csv(invalid_csv_rows)

    def test_process_votes_csv_row(self):
        tz = timezone("Etc/UTC")

        row = [
            "4/1/2024 9:00:00",
            "https://example.com/1",
            "https://example.com/2",
            "https://example.com/3",
            "https://example.com/4",
            "https://example.com/5",
            "https://example.com/6",
            "https://example.com/7",
        ]
        ballot = process_votes_csv_row(row)

        self.assertEqual("2024-04-01T09:00:00", ballot.timestamp.isoformat())
        self.assertEqual(7, len(ballot.votes))
        self.assertEqual("https://example.com/1", ballot.votes[0].url)
        self.assertEqual("https://example.com/2", ballot.votes[1].url)
        self.assertEqual("https://example.com/3", ballot.votes[2].url)
        self.assertEqual("https://example.com/4", ballot.votes[3].url)
        self.assertEqual("https://example.com/5", ballot.votes[4].url)
        self.assertEqual("https://example.com/6", ballot.votes[5].url)
        self.assertEqual("https://example.com/7", ballot.votes[6].url)

    def test_validate_video_data(self):
        data = {
            "title": "Example Video 1",
            "uploader": "Example Uploader",
            "upload_date": datetime(2024, 4, 1, 9, 0, 0),
            "duration": 300,
        }
        missing_fields = validate_video_data(data)
        self.assertEqual(0, len(missing_fields))

        data = {
            "uploader": "Example Uploader",
            "upload_date": datetime(2024, 4, 1, 9, 0, 0),
            "duration": 300,
        }
        missing_fields = validate_video_data(data)
        self.assertEqual(1, len(missing_fields))
        self.assertEqual("title", missing_fields[0])

        data = {}
        missing_fields = validate_video_data(data)
        self.assertEqual(4, len(missing_fields))
        self.assertEqual("title", missing_fields[0])
        self.assertEqual("uploader", missing_fields[1])
        self.assertEqual("upload_date", missing_fields[2])
        self.assertEqual("duration", missing_fields[3])

    def test_generate_annotated_csv_data(self):
        ballots = [
            # Ballot with 10 votes, some annotated
            Ballot(
                datetime(2024, 4, 1, 9, 0, 0),
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
            # Ballot with 5 votes, none annotated
            Ballot(
                datetime(2024, 4, 2, 9, 0, 0),
                [
                    Vote("https://example.com/1"),
                    Vote("https://example.com/3"),
                    Vote("https://example.com/5"),
                    Vote("https://example.com/7"),
                    Vote("https://example.com/9"),
                ],
            ),
            # Ballot with 1 vote
            Ballot(
                datetime(2024, 4, 3, 9, 0, 0),
                [
                    Vote("https://example.com/1"),
                ],
            ),
            # Ballot with 0 votes
            Ballot(datetime(2024, 4, 4, 9, 0, 0), []),
        ]

        videos = {
            "https://example.com/1": Video({"title": "Example Video 1"}),
            "https://example.com/2": Video({"title": "Example Video 2"}),
            "https://example.com/3": Video({"title": "Example Video 3"}),
            "https://example.com/4": Video({"title": "Example Video 4"}),
            "https://example.com/5": Video({"title": "Example Video 5"}),
            "https://example.com/6": Video({"title": "Example Video 6"}),
            "https://example.com/7": Video({"title": "Example Video 7"}),
            "https://example.com/8": Video({"title": "Example Video 8"}),
            "https://example.com/9": Video({"title": "Example Video 9"}),
            # Video with no data
            "https://example.com/10": Video(),
        }
        ballots[0].votes[0].annotations.add("VIDEO TOO OLD")
        ballots[0].votes[0].annotations.add("VIDEO TOO SHORT")
        ballots[0].votes[1].annotations.add("VIDEO TOO NEW")

        csv_rows = generate_annotated_csv_data(ballots, videos)

        self.assertEqual(5, len(csv_rows))
        self.assertEqual(22, len(csv_rows[0]))
        self.assertEqual(22, len(csv_rows[1]))
        self.assertEqual(22, len(csv_rows[2]))
        self.assertEqual(22, len(csv_rows[3]))
        self.assertEqual(22, len(csv_rows[4]))

        # Row 0
        self.assertEqual("Timestamp", csv_rows[0][0])
        for i in range(1, 21):
            self.assertEqual("", csv_rows[0][i])

        # Row 1
        self.assertEqual("4/1/2024 9:00:00", csv_rows[1][0])
        self.assertEqual("", csv_rows[1][1])
        self.assertEqual("Example Video 1", csv_rows[1][2])
        self.assertEqual("[VIDEO TOO OLD][VIDEO TOO SHORT]", csv_rows[1][3])
        self.assertEqual("Example Video 2", csv_rows[1][4])
        self.assertEqual("[VIDEO TOO NEW]", csv_rows[1][5])
        self.assertEqual("Example Video 3", csv_rows[1][6])
        self.assertEqual("", csv_rows[1][7])
        self.assertEqual("Example Video 4", csv_rows[1][8])
        self.assertEqual("", csv_rows[1][9])
        self.assertEqual("Example Video 5", csv_rows[1][10])
        self.assertEqual("", csv_rows[1][11])
        self.assertEqual("Example Video 6", csv_rows[1][12])
        self.assertEqual("", csv_rows[1][13])
        self.assertEqual("Example Video 7", csv_rows[1][14])
        self.assertEqual("", csv_rows[1][15])
        self.assertEqual("Example Video 8", csv_rows[1][16])
        self.assertEqual("", csv_rows[1][17])
        self.assertEqual("Example Video 9", csv_rows[1][18])
        self.assertEqual("", csv_rows[1][19])
        # For the last row, since the video has no data, by convention the vote
        # URL should be included instead.
        self.assertEqual("https://example.com/10", csv_rows[1][20])
        self.assertEqual("", csv_rows[1][21])

        # Row 2
        self.assertEqual("4/2/2024 9:00:00", csv_rows[2][0])
        self.assertEqual("", csv_rows[2][1])
        self.assertEqual("Example Video 1", csv_rows[2][2])
        self.assertEqual("", csv_rows[2][3])
        self.assertEqual("Example Video 3", csv_rows[2][4])
        self.assertEqual("", csv_rows[2][5])
        self.assertEqual("Example Video 5", csv_rows[2][6])
        self.assertEqual("", csv_rows[2][7])
        self.assertEqual("Example Video 7", csv_rows[2][8])
        self.assertEqual("", csv_rows[2][9])
        self.assertEqual("Example Video 9", csv_rows[2][10])
        for i in range(11, 22):
            self.assertEqual("", csv_rows[2][i])

        # Row 3
        self.assertEqual("4/3/2024 9:00:00", csv_rows[3][0])
        self.assertEqual("", csv_rows[3][1])
        self.assertEqual("Example Video 1", csv_rows[3][2])
        for i in range(3, 22):
            self.assertEqual("", csv_rows[3][i])

        # Row 4
        self.assertEqual("4/4/2024 9:00:00", csv_rows[4][0])
        for i in range(1, 22):
            self.assertEqual("", csv_rows[4][i])
