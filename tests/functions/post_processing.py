from unittest import TestCase
from datetime import datetime
from functions.post_processing import generate_archive_records, generate_sharable_records, generate_showcase_description

class MockFetcher:
    """Mock fetcher which returns a series of fake videos with increasing
    numbers."""
    def __init__(self):
        self.state = 1

    def fetch(self, url: str) -> dict:
        data = {
            'title': f'Example Video {self.state}',
            'uploader': f'Example Uploader {self.state}',
            'upload_date': datetime(2024, 4, self.state if self.state < 28 else 28),
        }

        self.state += 1

        return data

class TestFunctionsPostProcessing(TestCase):
    def test_generate_archive_records(self):
        urls = [
            'https://example.com/1',
            'https://example.com/2',
            'https://example.com/3',
        ]

        videos_data = {
            'https://example.com/1': {
                'title': 'Example Video 1',
                'uploader': 'Example Uploader 1',
                'upload_date': datetime(2024, 4, 1),
            },
            'https://example.com/2': {
                'title': 'Example Video 2',
                'uploader': 'Example Uploader 2',
                'upload_date': datetime(2024, 4, 2),
            },
            'https://example.com/3': {
                'title': 'Example Video 3',
                'uploader': 'Example Uploader 3',
                'upload_date': datetime(2024, 4, 3),
            },
        }
            
        records = generate_archive_records(urls, videos_data)

        self.assertEqual(3, len(records))

        self.assertEqual(2024, records[0]['year'])
        self.assertEqual(4, records[0]['month'])
        self.assertEqual('', records[0]['rank'])
        self.assertEqual('https://example.com/1', records[0]['link'])
        self.assertEqual('Example Video 1', records[0]['title'])
        self.assertEqual('Example Uploader 1', records[0]['channel'])
        self.assertEqual('2024-04-01', records[0]['upload date'])
        self.assertEqual('', records[0]['state'])
        self.assertEqual('https://example.com/1', records[0]['alternate link'])
        self.assertEqual('', records[0]['found'])
        self.assertEqual('', records[0]['notes'])

        self.assertEqual(2024, records[1]['year'])
        self.assertEqual(4, records[1]['month'])
        self.assertEqual('', records[1]['rank'])
        self.assertEqual('https://example.com/2', records[1]['link'])
        self.assertEqual('Example Video 2', records[1]['title'])
        self.assertEqual('Example Uploader 2', records[1]['channel'])
        self.assertEqual('2024-04-02', records[1]['upload date'])
        self.assertEqual('', records[1]['state'])
        self.assertEqual('https://example.com/2', records[1]['alternate link'])
        self.assertEqual('', records[1]['found'])
        self.assertEqual('', records[1]['notes'])

        self.assertEqual(2024, records[2]['year'])
        self.assertEqual(4, records[2]['month'])
        self.assertEqual('', records[2]['rank'])
        self.assertEqual('https://example.com/3', records[2]['link'])
        self.assertEqual('Example Video 3', records[2]['title'])
        self.assertEqual('Example Uploader 3', records[2]['channel'])
        self.assertEqual('2024-04-03', records[2]['upload date'])
        self.assertEqual('', records[2]['state'])
        self.assertEqual('https://example.com/3', records[2]['alternate link'])
        self.assertEqual('', records[2]['found'])
        self.assertEqual('', records[2]['notes'])

    def test_generate_sharable_records(self):
        urls = [
            'https://example.com/1',
            'https://example.com/2',
            'https://example.com/3',
        ]

        videos_data = {
            'https://example.com/1': {
                'title': 'Example Video 1',
                'uploader': 'Example Uploader 1',
                'upload_date': datetime(2024, 4, 1),
            },
            'https://example.com/2': {
                'title': 'Example Video 2',
                'uploader': 'Example Uploader 2',
                'upload_date': datetime(2024, 4, 2),
            },
            'https://example.com/3': {
                'title': 'Example Video 3',
                'uploader': 'Example Uploader 3',
                'upload_date': datetime(2024, 4, 3),
            },
        }
            
        records = generate_sharable_records(urls, videos_data)

        self.assertEqual(3, len(records))

        self.assertEqual('', records[0]['Rank'])
        self.assertEqual('Example Video 1', records[0]['Title'])
        self.assertEqual('=VLOOKUP("https://example.com/1", IMPORTRANGE("https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit", "top10!D:I"), 6, FALSE)', records[0]['Link'])
        self.assertEqual('', records[0]['Votes'])
        self.assertEqual('', records[0]['Popularity'])
        self.assertEqual('', records[0]['Total voters'])
        self.assertEqual('', records[0]['Notes'])

        self.assertEqual('', records[1]['Rank'])
        self.assertEqual('Example Video 2', records[1]['Title'])
        self.assertEqual('=VLOOKUP("https://example.com/2", IMPORTRANGE("https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit", "top10!D:I"), 6, FALSE)', records[1]['Link'])
        self.assertEqual('', records[1]['Votes'])
        self.assertEqual('', records[1]['Popularity'])
        self.assertEqual('', records[1]['Total voters'])
        self.assertEqual('', records[1]['Notes'])

        self.assertEqual('', records[2]['Rank'])
        self.assertEqual('Example Video 3', records[2]['Title'])
        self.assertEqual('=VLOOKUP("https://example.com/3", IMPORTRANGE("https://docs.google.com/spreadsheets/d/1rEofPkliKppvttd8pEX8H6DtSljlfmQLdFR-SlyyX7E/edit", "top10!D:I"), 6, FALSE)', records[2]['Link'])
        self.assertEqual('', records[2]['Votes'])
        self.assertEqual('', records[2]['Popularity'])
        self.assertEqual('', records[2]['Total voters'])
        self.assertEqual('', records[2]['Notes'])

    def test_generate_showcase_description(self):
        urls = [
            'https://example.com/1',
            'https://example.com/2',
            'https://example.com/3',
        ]

        videos_data = {
            'https://example.com/1': {
                'title': 'Example Video 1',
                'uploader': 'Example Uploader 1',
                'upload_date': datetime(2024, 4, 1),
            },
            'https://example.com/2': {
                'title': 'Example Video 2',
                'uploader': 'Example Uploader 2',
                'upload_date': datetime(2024, 4, 2),
            },
            'https://example.com/3': {
                'title': 'Example Video 3',
                'uploader': 'Example Uploader 3',
                'upload_date': datetime(2024, 4, 3),
            },
        }

        desc = generate_showcase_description(urls, videos_data, True)

        self.assertIn("Be sure to check out the videos in the description below! ", desc)
        self.assertIn('Example Video 1', desc)
        self.assertIn('https://example.com/1', desc)
        self.assertIn('Example Uploader 1', desc)
        self.assertIn('Example Video 2', desc)
        self.assertIn('https://example.com/2', desc)
        self.assertIn('Example Uploader 2', desc)
        self.assertIn('Example Video 3', desc)
        self.assertIn('https://example.com/3', desc)
        self.assertIn('Example Uploader 3', desc)

        self.assertIn('The Top 10 Pony Videos of April 2019', desc)
        self.assertIn('The Top 10 Pony Videos of April 2014', desc)

        self.assertIn('Fuck YouTube', desc)
