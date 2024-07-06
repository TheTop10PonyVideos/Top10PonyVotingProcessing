from unittest import TestCase
from datetime import datetime
from functions.post_processing import (
    generate_archive_records,
    generate_sharable_records,
    generate_showcase_description,
    create_videos_desc,
)


class TestFunctionsPostProcessing(TestCase):
    def test_generate_archive_records(self):
        top_10_records = [
            {
                'Title': 'Example 1',
                'Percentage': '90.0000%',
                'Total Votes': '18',
                'URL': 'https://example.com/1',
                'Notes': ''
            },
            {
                'Title': 'Example 2',
                'Percentage': '80.0000%',
                'Total Votes': '16',
                'URL': 'https://example.com/2',
                'Notes': 'Tie broken by random choice'
            },
            {
                'Title': 'Example 3',
                'Percentage': '80.0000%',
                'Total Votes': '16',
                'URL': 'https://example.com/3',
                'Notes': 'Tie broken by random choice'
            },
        ]

        videos_data = {
            'https://example.com/1': {
                'title': 'Example 1',
                'uploader': 'Uploader 1',
                'upload_date': datetime(2024, 4, 1),
            },
            'https://example.com/2': {
                'title': 'Example 2',
                'uploader': 'Uploader 2',
                'upload_date': datetime(2024, 4, 2),
            },
            'https://example.com/3': {
                'title': 'Example 3',
                'uploader': 'Uploader 3',
                'upload_date': datetime(2024, 4, 3),
            },
        }

        records = generate_archive_records(top_10_records, videos_data)

        self.assertEqual(3, len(records))

        self.assertEqual(2024, records[0]["year"])
        self.assertEqual(4, records[0]["month"])
        self.assertEqual(3, records[0]["rank"])
        self.assertEqual("https://example.com/3", records[0]["link"])
        self.assertEqual("Example 3", records[0]["title"])
        self.assertEqual("Uploader 3", records[0]["channel"])
        self.assertEqual("2024-04-03", records[0]["upload date"])
        self.assertEqual("", records[0]["state"])
        self.assertEqual("https://example.com/3", records[0]["alternate link"])
        self.assertEqual("", records[0]["found"])
        self.assertEqual("", records[0]["notes"])

        self.assertEqual(2024, records[1]["year"])
        self.assertEqual(4, records[1]["month"])
        self.assertEqual(2, records[1]["rank"])
        self.assertEqual("https://example.com/2", records[1]["link"])
        self.assertEqual("Example 2", records[1]["title"])
        self.assertEqual("Uploader 2", records[1]["channel"])
        self.assertEqual("2024-04-02", records[1]["upload date"])
        self.assertEqual("", records[1]["state"])
        self.assertEqual("https://example.com/2", records[1]["alternate link"])
        self.assertEqual("", records[1]["found"])
        self.assertEqual("", records[1]["notes"])

        self.assertEqual(2024, records[2]["year"])
        self.assertEqual(4, records[2]["month"])
        self.assertEqual(1, records[2]["rank"])
        self.assertEqual("https://example.com/1", records[2]["link"])
        self.assertEqual("Example 1", records[2]["title"])
        self.assertEqual("Uploader 1", records[2]["channel"])
        self.assertEqual("2024-04-01", records[2]["upload date"])
        self.assertEqual("", records[2]["state"])
        self.assertEqual("https://example.com/1", records[2]["alternate link"])
        self.assertEqual("", records[2]["found"])
        self.assertEqual("", records[2]["notes"])



    def test_generate_sharable_records(self):
        top_10_records = [
            {
                'Title': 'Example 1',
                'Percentage': '90.0000%',
                'Total Votes': '18',
                'URL': 'https://example.com/1',
                'Notes': ''
            },
            {
                'Title': 'Example 2',
                'Percentage': '80.0000%',
                'Total Votes': '16',
                'URL': 'https://example.com/2',
                'Notes': 'Tie broken by random choice'
            },
            {
                'Title': 'Example 3',
                'Percentage': '80.0000%',
                'Total Votes': '16',
                'URL': 'https://example.com/3',
                'Notes': 'Tie broken by random choice'
            },
        ]

        hm_records = [
            {
                'Title': 'Example 4',
                'Percentage': '60.0000%',
                'Total Votes': '12',
                'URL': 'https://example.com/4',
                'Notes': 'Missed out on top 10 due to tie break'
            },
            {
                'Title': 'Example 5',
                'Percentage': '50.0000%',
                'Total Votes': '10',
                'URL': 'https://example.com/5',
                'Notes': ''
            },
        ]

        records = generate_sharable_records(top_10_records, hm_records)

        self.assertEqual(5, len(records))

        self.assertEqual(1, records[0]["Rank"])
        self.assertEqual("Example 1", records[0]["Title"])
        self.assertEqual(
            '=VLOOKUP("https://example.com/1", IMPORTRANGE("https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit", "top10!D:I"), 6, FALSE)',
            records[0]["Link"],
        )
        self.assertEqual('18', records[0]["Votes"])
        self.assertEqual("90.0000%", records[0]["Popularity"])
        self.assertEqual(20, records[0]["Total voters"])
        self.assertEqual("", records[0]["Notes"])

        self.assertEqual(2, records[1]["Rank"])
        self.assertEqual("Example 2", records[1]["Title"])
        self.assertEqual(
            '=VLOOKUP("https://example.com/2", IMPORTRANGE("https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit", "top10!D:I"), 6, FALSE)',
            records[1]["Link"],
        )
        self.assertEqual('16', records[1]["Votes"])
        self.assertEqual("80.0000%", records[1]["Popularity"])
        self.assertEqual(20, records[1]["Total voters"])
        self.assertEqual("Tie broken by random choice", records[1]["Notes"])

        self.assertEqual(3, records[2]["Rank"])
        self.assertEqual("Example 3", records[2]["Title"])
        self.assertEqual(
            '=VLOOKUP("https://example.com/3", IMPORTRANGE("https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit", "top10!D:I"), 6, FALSE)',
            records[2]["Link"],
        )
        self.assertEqual('16', records[2]["Votes"])
        self.assertEqual("80.0000%", records[2]["Popularity"])
        self.assertEqual(20, records[2]["Total voters"])
        self.assertEqual("Tie broken by random choice", records[2]["Notes"])

        self.assertEqual('HM', records[3]["Rank"])
        self.assertEqual("Example 4", records[3]["Title"])
        self.assertEqual(
            '=VLOOKUP("https://example.com/4", IMPORTRANGE("https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit", "top10!D:I"), 6, FALSE)',
            records[3]["Link"],
        )
        self.assertEqual('12', records[3]["Votes"])
        self.assertEqual("60.0000%", records[3]["Popularity"])
        self.assertEqual(20, records[3]["Total voters"])
        self.assertEqual("HM. Missed out on top 10 due to tie break", records[3]["Notes"])

        self.assertEqual('HM', records[4]["Rank"])
        self.assertEqual("Example 5", records[4]["Title"])
        self.assertEqual(
            '=VLOOKUP("https://example.com/5", IMPORTRANGE("https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit", "top10!D:I"), 6, FALSE)',
            records[4]["Link"],
        )
        self.assertEqual('10', records[4]["Votes"])
        self.assertEqual("50.0000%", records[4]["Popularity"])
        self.assertEqual(20, records[4]["Total voters"])
        self.assertEqual("HM", records[4]["Notes"])


    def test_generate_showcase_description(self):
        top_10_records = [
            {
                'Title': 'Top 10 Video 1',
                'Percentage': '90.0000%',
                'Total Votes': '18',
                'URL': 'https://example.com/1',
                'Notes': ''
            },
            {
                'Title': 'Top 10 Video 2',
                'Percentage': '80.0000%',
                'Total Votes': '16',
                'URL': 'https://example.com/2',
                'Notes': 'Tie broken by random choice'
            },
            {
                'Title': 'Top 10 Video 3',
                'Percentage': '80.0000%',
                'Total Votes': '16',
                'URL': 'https://example.com/3',
                'Notes': 'Tie broken by random choice'
            },
        ]

        hm_records = [
            {
                'Title': 'Honorable mention 1',
                'Percentage': '60.0000%',
                'Total Votes': '12',
                'URL': 'https://example.com/hm1',
                'Notes': 'Missed out on top 10 due to tie break'
            },
            {
                'Title': 'Honorable mention 2',
                'Percentage': '50.0000%',
                'Total Votes': '10',
                'URL': 'https://example.com/hm2',
                'Notes': ''
            },
        ]

        history_records = {
            '1 year ago': [
                {
                    'Title': 'History 1',
                    'Percentage': '10.0000%',
                    'Total Votes': '2',
                    'URL': 'https://example.com/hist1',
                    'Notes': ''
                },
                {
                    'Title': 'History 2',
                    'Percentage': '10.0000%',
                    'Total Votes': '2',
                    'URL': 'https://example.com/hist2',
                    'Notes': ''
                },
            ],
            '3 years ago': [
                {
                    'Title': 'History 3',
                    'Percentage': '10.0000%',
                    'Total Votes': '2',
                    'URL': 'https://example.com/hist3',
                    'Notes': ''
                },
                {
                    'Title': 'History 4',
                    'Percentage': '10.0000%',
                    'Total Votes': '2',
                    'URL': 'https://example.com/hist4',
                    'Notes': ''
                },
            ],
            '5 years ago': [
                {
                    'Title': 'History 5',
                    'Percentage': '10.0000%',
                    'Total Votes': '2',
                    'URL': 'https://example.com/hist5',
                    'Notes': ''
                },
                {
                    'Title': 'History 6',
                    'Percentage': '10.0000%',
                    'Total Votes': '2',
                    'URL': 'https://example.com/hist6',
                    'Notes': ''
                },
            ],
        }

        top_10_videos_data = {
            'https://example.com/1': {
                'title': 'Top 10 Video 1',
                'uploader': 'Uploader 1',
                'upload_date': datetime(2024, 4, 1),
            },
            'https://example.com/2': {
                'title': 'Top 10 Video 2',
                'uploader': 'Uploader 2',
                'upload_date': datetime(2024, 4, 2),
            },
            'https://example.com/3': None
        }

        hm_videos_data = {
            'https://example.com/hm1': {
                'title': 'Honorable mention 1',
                'uploader': 'Uploader HM1',
                'upload_date': datetime(2024, 4, 1),
            },
            'https://example.com/hm2': {
                'title': 'Honorable mention 2',
                'uploader': 'Uploader HM2',
                'upload_date': datetime(2024, 4, 2),
            },
        }

        history_videos_data = {
            'https://example.com/hist1': {
                'title': 'History 1',
                'uploader': 'Uploader H1',
                'upload_date': datetime(2024, 4, 1),
            },
            'https://example.com/hist2': {
                'title': 'History 2',
                'uploader': 'Uploader H2',
                'upload_date': datetime(2024, 4, 2),
            },
            'https://example.com/hist3': {
                'title': 'History 3',
                'uploader': 'Uploader H3',
                'upload_date': datetime(2024, 4, 3),
            },
            'https://example.com/hist4': {
                'title': 'History 4',
                'uploader': 'Uploader H4',
                'upload_date': datetime(2024, 4, 4),
            },
            'https://example.com/hist5': {
                'title': 'History 5',
                'uploader': 'Uploader H5',
                'upload_date': datetime(2024, 4, 5),
            },
            'https://example.com/hist6': {
                'title': 'History 6',
                'uploader': 'Uploader H6',
                'upload_date': datetime(2024, 4, 6),
            },
        }

        desc = generate_showcase_description(top_10_records, hm_records, history_records, top_10_videos_data, hm_videos_data, history_videos_data, True)

        # Top 10 Video 3 had no video data, but it should still appear in the
        # description as the function will automatically source the data from
        # the supplied record. However, it won't have an uploader.
        self.assertIn(
            "Be sure to check out the videos in the description below! ", desc
        )
        self.assertIn("Top 10 Video 1", desc)
        self.assertIn("https://example.com/1", desc)
        self.assertIn("Uploader 1", desc)
        self.assertIn("Top 10 Video 2", desc)
        self.assertIn("https://example.com/2", desc)
        self.assertIn("Uploader 2", desc)
        self.assertIn("Top 10 Video 3", desc)
        self.assertIn("https://example.com/3", desc)

        self.assertIn("The Top 10 Pony Videos of April 2023", desc)
        self.assertIn("The Top 10 Pony Videos of April 2021", desc)
        self.assertIn("The Top 10 Pony Videos of April 2019", desc)

        self.assertIn("Fuck YouTube", desc)


    def test_create_videos_desc(self):
        records = [
            {
                'Title': 'Honorable mention 1',
                'Percentage': '20.0000%',
                'Total Votes': '2',
                'URL': 'https://example.com/hm1',
                'Notes': ''
            },
            {
                'Title': 'Honorable mention 2',
                'Percentage': '10.0000%',
                'Total Votes': '1',
                'URL': 'https://example.com/hm2',
                'Notes': ''
            },
        ]

        videos_data = {
            'https://example.com/hm1': {
                'title': 'Honorable mention 1',
                'uploader': 'Uploader 1',
                'upload_date': datetime(2024, 4, 1),
            },
            'https://example.com/hm2': {
                'title': 'Honorable mention 2',
                'uploader': 'Uploader 2',
                'upload_date': datetime(2024, 4, 2),
            },
        }

        desc = create_videos_desc(records, videos_data)

        self.assertEqual("""○ Honorable mention 1
https://example.com/hm1
Uploader 1

○ Honorable mention 2
https://example.com/hm2
Uploader 2
""", desc)
