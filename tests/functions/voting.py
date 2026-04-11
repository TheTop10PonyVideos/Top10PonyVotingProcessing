from unittest import TestCase
from datetime import datetime
from pytz import timezone
from functions.voting import (
    normalize_voting_data,
    process_voting_data,
    process_votes_csv_row,
    validate_video_data,
    generate_annotated_csv_data,
    shift_columns,
)
from classes.voting import Ballot, Vote, Video
import pandas as pd


class TestFunctionsVoting(TestCase):
    def test_normalize_voting_data(self):
        voting_data = pd.DataFrame([
            [
                "4/1/2024 9:00:00",
                "https://example.com/1",
                "https://www.youtube.com/watch?v=9RT4lfvVFhA",
                "https://www.youtube.com/live/Q8k4UTf8jiI",
                "https://youtu.be/9RT4lfvVFhA",
                "https://youtube.com/watch?v=9RT4lfvVFhA",
                "https://m.youtube.com/watch?v=9RT4lfvVFhA",
                "https://www.bilibili.com/video/BV1HC411H7Po/",
                "https://pony.tube/w/bYSyWpjg6r6zo68o1imK5t",
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
                "",
            ],
        ], columns=["Timestamp", "", "", "", "", "", "", "", "", "", ""]
        )

        norm_voting_data = normalize_voting_data(voting_data)
        self.assertEqual((2, 11), norm_voting_data.shape)
        self.assertEqual("Timestamp", norm_voting_data.columns[0])
        self.assertTrue(([
            "4/1/2024 9:00:00",
            "https://example.com/1",
            "https://www.youtube.com/watch?v=9RT4lfvVFhA",
            "https://www.youtube.com/watch?v=Q8k4UTf8jiI",
            "https://www.youtube.com/watch?v=9RT4lfvVFhA",
            "https://www.youtube.com/watch?v=9RT4lfvVFhA",
            "https://www.youtube.com/watch?v=9RT4lfvVFhA",
            "https://www.bilibili.com/video/BV1HC411H7Po/",
            "https://pony.tube/w/bYSyWpjg6r6zo68o1imK5t",
            "",
            ""
        ] == norm_voting_data.loc[0]).all())

        self.assertTrue(([
            "12/31/2024 23:59:59",
            "https://example.com/2",
            ""
        ] == norm_voting_data.iloc[1, :3]).all())

    def test_process_voting_data(self):
        tz = timezone("Etc/UTC")

        voting_data = pd.DataFrame([
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
        ], columns=['Timestamp'] + [''] * 9)
        voting_data['Timestamp'] = pd.to_datetime(voting_data['Timestamp'], format='%m/%d/%Y %H:%M:%S')

        ballots = process_voting_data(voting_data)
        self.assertEqual(4, len(ballots))
        self.assertEqual("2024-04-01T09:00:00", ballots[0].timestamp.isoformat())
        self.assertEqual("2024-12-31T23:59:59", ballots[1].timestamp.isoformat())
        self.assertEqual("2022-02-02T02:02:02", ballots[2].timestamp.isoformat())
        self.assertEqual("2023-11-06T10:23:36", ballots[3].timestamp.isoformat())

        invalid_csv_rows = pd.DataFrame([
            ["Invalid", "", "", "", "", "", "", "", "", "", ""],
            ["Invalid", "", "", "", "", "", "", "", "", "", ""],
            ["Invalid", "", "", "", "", "", "", "", "", "", ""],
        ], columns=[''] * 11)

        with self.assertRaises(ValueError):
            ballots = process_voting_data(invalid_csv_rows)

    def test_process_votes_csv_row(self):
        tz = timezone("Etc/UTC")

        df = pd.DataFrame([[
            "4/1/2024 9:00:00",
            "https://example.com/1",
            "https://example.com/2",
            "https://example.com/3",
            "https://example.com/4",
            "https://example.com/5",
            "https://example.com/6",
            "https://example.com/7",
        ]], columns=['Timestamp'] + [''] * 7)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%m/%d/%Y %H:%M:%S')
        ballot = process_votes_csv_row(df.loc[0])

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
            "platform": "PonyTube"
        }
        missing_fields = validate_video_data(data)
        self.assertEqual(0, len(missing_fields))

        data = {
            "uploader": "Example Uploader",
            "upload_date": datetime(2024, 4, 1, 9, 0, 0),
            "duration": 300,
            "platform": "PonyTube"
        }
        missing_fields = validate_video_data(data)
        self.assertEqual(1, len(missing_fields))
        self.assertEqual("title", missing_fields[0])

        data = {}
        missing_fields = validate_video_data(data)
        self.assertEqual(5, len(missing_fields))
        self.assertEqual("title", missing_fields[0])
        self.assertEqual("uploader", missing_fields[1])
        self.assertEqual("upload_date", missing_fields[2])
        self.assertEqual("duration", missing_fields[3])
        self.assertEqual("platform", missing_fields[4])

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

        csv_df = generate_annotated_csv_data(ballots, videos)

        self.assertEqual((4, 22), csv_df.shape)

        # Header
        self.assertEqual("Timestamp", csv_df.columns[0])
        self.assertTrue((csv_df.columns[1:] == '').all())

        # Row 1
        self.assertTrue(([
            "4/1/2024 9:00:00",
            "",
            "Example Video 1",
            "[VIDEO TOO OLD][VIDEO TOO SHORT]",
            "Example Video 2",
            "[VIDEO TOO NEW]",
            "Example Video 3",
            "",
            "Example Video 4",
            "",
            "Example Video 5",
            "",
            "Example Video 6",
            "",
            "Example Video 7",
            "",
            "Example Video 8",
            "",
            "Example Video 9",
            ""
        ] == csv_df.iloc[0, :-2]).all())
        # For the last column, since the video has no data, by convention the vote
        # URL should be included instead.
        self.assertEqual("https://example.com/10", csv_df.iloc[0, 20])
        self.assertEqual("", csv_df.iloc[0, 21])

        # Row 2
        self.assertTrue(([
            "4/2/2024 9:00:00",
            "",
            "Example Video 1",
            "",
            "Example Video 3",
            "",
            "Example Video 5",
            "",
            "Example Video 7",
            "",
            "Example Video 9"
        ] == csv_df.iloc[1, :11]).all())

        self.assertTrue((csv_df.iloc[1, 11:] == '').all())

        # Row 3
        self.assertTrue(([
            "4/3/2024 9:00:00",
            "",
            "Example Video 1"
        ] == csv_df.iloc[2, :3]).all())

        self.assertTrue((csv_df.iloc[2, 3:] == '').all())

        # Row 4
        self.assertEqual("4/4/2024 9:00:00", csv_df.iloc[3, 0])
        self.assertTrue((csv_df.iloc[3, 1:] == '').all())

    def test_shift_columns(self):
        rows = pd.DataFrame([
            ["a", "b", "c"],
            ["d", "e", "f"],
            ["g", "h", "i"],
        ])

        rows_shifted = shift_columns(rows)
        self.assertEqual((3, 6), rows_shifted.shape)

        self.assertEqual("a", rows_shifted.iloc[0, 0])
        self.assertEqual("", rows_shifted.iloc[0, 1])
        self.assertEqual("b", rows_shifted.iloc[0, 2])
        self.assertEqual("", rows_shifted.iloc[0, 3])
        self.assertEqual("c", rows_shifted.iloc[0, 4])
        self.assertEqual("", rows_shifted.iloc[0, 5])
        self.assertEqual("d", rows_shifted.iloc[1, 0])
        self.assertEqual("", rows_shifted.iloc[1, 1])
        self.assertEqual("e", rows_shifted.iloc[1, 2])
        self.assertEqual("", rows_shifted.iloc[1, 3])
        self.assertEqual("f", rows_shifted.iloc[1, 4])
        self.assertEqual("", rows_shifted.iloc[1, 5])
        self.assertEqual("g", rows_shifted.iloc[2, 0])
        self.assertEqual("", rows_shifted.iloc[2, 1])
        self.assertEqual("h", rows_shifted.iloc[2, 2])
        self.assertEqual("", rows_shifted.iloc[2, 3])
        self.assertEqual("i", rows_shifted.iloc[2, 4])
        self.assertEqual("", rows_shifted.iloc[2, 5])
