from unittest import TestCase
from datetime import datetime
from functions.post_processing import (
    create_post_processed_records,
    generate_archive_records,
    generate_sharable_records,
    generate_showcase_description,
)


class TestFunctionsPostProcessing(TestCase):
    def test_create_post_processed_records(self):
        # 4 video data records, for which two are tied at 2nd place
        calc_records = [
            {
                "Title": "Example Video 1",
                "Percentage": "69.7368%",
                "Total Votes": "53",
                "URL": "https://example.com/1",
            },
            {
                "Title": "Example Video 2",
                "Percentage": "11.8421%",
                "Total Votes": "9",
                "URL": "https://example.com/2",
            },
            {
                "Title": "Example Video 3",
                "Percentage": "11.8421%",
                "Total Votes": "9",
                "URL": "https://example.com/3",
            },
            {
                "Title": "Example Video 4",
                "Percentage": "6.5789%",
                "Total Votes": "5",
                "URL": "https://example.com/4",
            },
        ]

        # 3 video data records, the one for video 3 is missing
        videos_data = {
            "https://example.com/1": {
                "title": "Example Video 1",
                "uploader": "Example Uploader 1",
                "upload_date": datetime(2024, 4, 1),
            },
            "https://example.com/2": {
                "title": "Example Video 2",
                "uploader": "Example Uploader 2",
                "upload_date": datetime(2024, 4, 2),
            },
            "https://example.com/4": {
                "title": "Example Video 4",
                "uploader": "Example Uploader 4",
                "upload_date": datetime(2024, 4, 4),
            },
        }

        post_proc_records = create_post_processed_records(
            calc_records, videos_data, True
        )

        self.assertEqual(4, len(post_proc_records))

        self.assertEqual("https://example.com/1", post_proc_records[0]["url"])
        self.assertEqual("Example Uploader 1", post_proc_records[0]["uploader"])
        self.assertEqual(datetime(2024, 4, 1), post_proc_records[0]["upload_date"])
        self.assertEqual(1, post_proc_records[0]["rank"])
        self.assertEqual(53, post_proc_records[0]["votes"])
        self.assertEqual(69.7368, post_proc_records[0]["percentage"])
        self.assertEqual(76, post_proc_records[0]["total_voters"])

        self.assertEqual("https://example.com/2", post_proc_records[1]["url"])
        self.assertEqual("Example Uploader 2", post_proc_records[1]["uploader"])
        self.assertEqual(datetime(2024, 4, 2), post_proc_records[1]["upload_date"])
        self.assertEqual(2, post_proc_records[1]["rank"])
        self.assertEqual(9, post_proc_records[1]["votes"])
        self.assertEqual(11.8421, post_proc_records[1]["percentage"])
        self.assertEqual(76, post_proc_records[1]["total_voters"])

        self.assertEqual("https://example.com/3", post_proc_records[2]["url"])
        self.assertEqual(None, post_proc_records[2]["uploader"])
        self.assertEqual(None, post_proc_records[2]["upload_date"])
        self.assertEqual(2, post_proc_records[2]["rank"])
        self.assertEqual(9, post_proc_records[2]["votes"])
        self.assertEqual(11.8421, post_proc_records[2]["percentage"])
        self.assertEqual(76, post_proc_records[2]["total_voters"])

        self.assertEqual("https://example.com/4", post_proc_records[3]["url"])
        self.assertEqual("Example Uploader 4", post_proc_records[3]["uploader"])
        self.assertEqual(datetime(2024, 4, 4), post_proc_records[3]["upload_date"])
        self.assertEqual(3, post_proc_records[3]["rank"])
        self.assertEqual(5, post_proc_records[3]["votes"])
        self.assertEqual(6.5789, post_proc_records[3]["percentage"])
        self.assertEqual(76, post_proc_records[3]["total_voters"])

    def test_generate_archive_records(self):
        post_proc_records = [
            {
                "url": "https://example.com/1",
                "title": "Example Video 1",
                "uploader": "Example Uploader 1",
                "upload_date": datetime(2024, 4, 1),
                "rank": 1,
                "votes": 53,
                "percentage": 69.7368,
                "total_voters": 76,
            },
            {
                "url": "https://example.com/2",
                "title": "Example Video 2",
                "uploader": "Example Uploader 2",
                "upload_date": datetime(2024, 4, 2),
                "rank": 2,
                "votes": 9,
                "percentage": 11.8421,
                "total_voters": 76,
            },
            {
                "url": "https://example.com/3",
                "title": "Example Video 3",
                "uploader": None,
                "upload_date": None,
                "rank": 2,
                "votes": 9,
                "percentage": 11.8421,
                "total_voters": 76,
            },
            {
                "url": "https://example.com/4",
                "title": "Example Video 4",
                "uploader": "Example Uploader 4",
                "upload_date": datetime(2024, 4, 4),
                "rank": 3,
                "votes": 5,
                "percentage": 6.5789,
                "total_voters": 76,
            },
        ]

        records = generate_archive_records(post_proc_records)

        self.assertEqual(4, len(records))

        self.assertEqual(2024, records[0]["year"])
        self.assertEqual(4, records[0]["month"])
        self.assertEqual(3, records[0]["rank"])
        self.assertEqual("https://example.com/4", records[0]["link"])
        self.assertEqual("Example Video 4", records[0]["title"])
        self.assertEqual("Example Uploader 4", records[0]["channel"])
        self.assertEqual("2024-04-04", records[0]["upload date"])
        self.assertEqual("", records[0]["state"])
        self.assertEqual("https://example.com/4", records[0]["alternate link"])
        self.assertEqual("", records[0]["found"])
        self.assertEqual("", records[0]["notes"])

        self.assertEqual("", records[1]["year"])
        self.assertEqual("", records[1]["month"])
        self.assertEqual(2, records[1]["rank"])
        self.assertEqual("https://example.com/3", records[1]["link"])
        self.assertEqual("Example Video 3", records[1]["title"])
        self.assertEqual("", records[1]["channel"])
        self.assertEqual("", records[1]["upload date"])
        self.assertEqual("", records[1]["state"])
        self.assertEqual("https://example.com/3", records[1]["alternate link"])
        self.assertEqual("", records[1]["found"])
        self.assertEqual("", records[1]["notes"])

        self.assertEqual(2024, records[2]["year"])
        self.assertEqual(4, records[2]["month"])
        self.assertEqual(2, records[2]["rank"])
        self.assertEqual("https://example.com/2", records[2]["link"])
        self.assertEqual("Example Video 2", records[2]["title"])
        self.assertEqual("Example Uploader 2", records[2]["channel"])
        self.assertEqual("2024-04-02", records[2]["upload date"])
        self.assertEqual("", records[2]["state"])
        self.assertEqual("https://example.com/2", records[2]["alternate link"])
        self.assertEqual("", records[2]["found"])
        self.assertEqual("", records[2]["notes"])

        self.assertEqual(2024, records[3]["year"])
        self.assertEqual(4, records[3]["month"])
        self.assertEqual(1, records[3]["rank"])
        self.assertEqual("https://example.com/1", records[3]["link"])
        self.assertEqual("Example Video 1", records[3]["title"])
        self.assertEqual("Example Uploader 1", records[3]["channel"])
        self.assertEqual("2024-04-01", records[3]["upload date"])
        self.assertEqual("", records[3]["state"])
        self.assertEqual("https://example.com/1", records[3]["alternate link"])
        self.assertEqual("", records[3]["found"])
        self.assertEqual("", records[3]["notes"])

    def test_generate_sharable_records(self):
        post_proc_records = [
            {
                "url": "https://example.com/1",
                "title": "Example Video 1",
                "uploader": "Example Uploader 1",
                "upload_date": datetime(2024, 4, 1),
                "rank": 1,
                "votes": 53,
                "percentage": 69.7368,
                "total_voters": 76,
            },
            {
                "url": "https://example.com/2",
                "title": "Example Video 2",
                "uploader": "Example Uploader 2",
                "upload_date": datetime(2024, 4, 2),
                "rank": 2,
                "votes": 9,
                "percentage": 11.8421,
                "total_voters": 76,
            },
            {
                "url": "https://example.com/3",
                "title": "Example Video 3",
                "uploader": None,
                "upload_date": None,
                "rank": 2,
                "votes": 9,
                "percentage": 11.8421,
                "total_voters": 76,
            },
            {
                "url": "https://example.com/4",
                "title": "Example Video 4",
                "uploader": "Example Uploader 4",
                "upload_date": datetime(2024, 4, 4),
                "rank": 3,
                "votes": 5,
                "percentage": 6.5789,
                "total_voters": 76,
            },
        ]

        records = generate_sharable_records(post_proc_records)

        self.assertEqual(4, len(records))

        self.assertEqual(1, records[0]["Rank"])
        self.assertEqual("Example Video 1", records[0]["Title"])
        self.assertEqual(
            '=VLOOKUP("https://example.com/1", IMPORTRANGE("https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit", "top10!D:I"), 6, FALSE)',
            records[0]["Link"],
        )
        self.assertEqual(53, records[0]["Votes"])
        self.assertEqual("69.7368%", records[0]["Popularity"])
        self.assertEqual(76, records[0]["Total voters"])
        self.assertEqual("", records[0]["Notes"])

        self.assertEqual(2, records[1]["Rank"])
        self.assertEqual("Example Video 2", records[1]["Title"])
        self.assertEqual(
            '=VLOOKUP("https://example.com/2", IMPORTRANGE("https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit", "top10!D:I"), 6, FALSE)',
            records[1]["Link"],
        )
        self.assertEqual(9, records[1]["Votes"])
        self.assertEqual("11.8421%", records[1]["Popularity"])
        self.assertEqual(76, records[1]["Total voters"])
        self.assertEqual("", records[1]["Notes"])

        self.assertEqual(2, records[2]["Rank"])
        self.assertEqual("Example Video 3", records[2]["Title"])
        self.assertEqual(
            '=VLOOKUP("https://example.com/3", IMPORTRANGE("https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit", "top10!D:I"), 6, FALSE)',
            records[2]["Link"],
        )
        self.assertEqual(9, records[2]["Votes"])
        self.assertEqual("11.8421%", records[2]["Popularity"])
        self.assertEqual(76, records[2]["Total voters"])
        self.assertEqual("", records[2]["Notes"])

        self.assertEqual(3, records[3]["Rank"])
        self.assertEqual("Example Video 4", records[3]["Title"])
        self.assertEqual(
            '=VLOOKUP("https://example.com/4", IMPORTRANGE("https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit", "top10!D:I"), 6, FALSE)',
            records[3]["Link"],
        )
        self.assertEqual(5, records[3]["Votes"])
        self.assertEqual("6.5789%", records[3]["Popularity"])
        self.assertEqual(76, records[3]["Total voters"])
        self.assertEqual("", records[3]["Notes"])

    def test_generate_showcase_description(self):
        post_proc_records = [
            {
                "url": "https://example.com/1",
                "title": "Example Video 1",
                "uploader": "Example Uploader 1",
                "upload_date": datetime(2024, 4, 1),
                "rank": 1,
                "votes": 53,
                "percentage": 69.7368,
                "total_voters": 76,
            },
            {
                "url": "https://example.com/2",
                "title": "Example Video 2",
                "uploader": "Example Uploader 2",
                "upload_date": datetime(2024, 4, 2),
                "rank": 2,
                "votes": 9,
                "percentage": 11.8421,
                "total_voters": 76,
            },
            {
                "url": "https://example.com/3",
                "title": "Example Video 3",
                "uploader": None,
                "upload_date": None,
                "rank": 2,
                "votes": 9,
                "percentage": 11.8421,
                "total_voters": 76,
            },
            {
                "url": "https://example.com/4",
                "title": "Example Video 4",
                "uploader": "Example Uploader 4",
                "upload_date": datetime(2024, 4, 4),
                "rank": 3,
                "votes": 5,
                "percentage": 6.5789,
                "total_voters": 76,
            },
        ]

        desc = generate_showcase_description(post_proc_records, True)

        # Example Video 3 shouldn't appear in the output, as it doesn't have
        # sufficient data (no upload date, no uploader)
        self.assertIn(
            "Be sure to check out the videos in the description below! ", desc
        )
        self.assertIn("Example Video 1", desc)
        self.assertIn("https://example.com/1", desc)
        self.assertIn("Example Uploader 1", desc)
        self.assertIn("Example Video 2", desc)
        self.assertIn("https://example.com/2", desc)
        self.assertIn("Example Uploader 2", desc)
        self.assertIn("Example Video 4", desc)
        self.assertIn("https://example.com/4", desc)
        self.assertIn("Example Uploader 4", desc)

        self.assertIn("The Top 10 Pony Videos of April 2019", desc)
        self.assertIn("The Top 10 Pony Videos of April 2014", desc)

        self.assertIn("Fuck YouTube", desc)
