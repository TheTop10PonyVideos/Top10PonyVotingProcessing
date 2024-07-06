from unittest import TestCase
from functions.top_10_parser import group_records_by_headings, parse_calculated_top_10_csv

class TestFunctionsTop10Parser(TestCase):
    def test_group_by_headings(self):
        records = [
            {'name': 'Example 1', 'value': '10'},
            {'name': 'Example 2', 'value': '20'},
            {'name': 'Example 3', 'value': '30'},
            {'name': 'Example 4', 'value': '40'},
            {'name': 'Heading 1', 'value': ''},
            {'name': 'Example 5', 'value': '50'},
            {'name': 'Example 6', 'value': '60'},
            {'name': 'Example 7', 'value': '70'},
            {'name': 'Heading 2', 'value': ''},
            {'name': 'Example 8', 'value': '80'},
            {'name': 'Example 9', 'value': '90'},
            {'name': 'Heading 3', 'value': ''},
            {'name': 'Example 10', 'value': '100'},
            {'name': 'Heading 4', 'value': ''},
        ]

        headings = ['Heading 1', 'Heading 2', 'Heading 3', 'Heading 4']

        grouped_records = group_records_by_headings(records, headings, 'name')
        self.assertEqual(5, len(grouped_records))

        self.assertIn('(NO HEADING)', grouped_records)
        self.assertIn('Heading 1', grouped_records)
        self.assertIn('Heading 2', grouped_records)
        self.assertIn('Heading 3', grouped_records)
        self.assertIn('Heading 4', grouped_records)

        self.assertEqual(4, len(grouped_records['(NO HEADING)']))
        self.assertEqual(3, len(grouped_records['Heading 1']))
        self.assertEqual(2, len(grouped_records['Heading 2']))
        self.assertEqual(1, len(grouped_records['Heading 3']))
        self.assertEqual(0, len(grouped_records['Heading 4']))

        self.assertEqual('Example 10', grouped_records['Heading 3'][0]['name'])

    def test_parse_calculated_top_10_csv(self):
        records = [
            {
                'Title': 'Example 1',
                'Percentage': '90.0000%',
                'Total Votes': '18',
                'URL': 'https://www.youtube.com/watch?v=dmVWvOC_2HU',
                'Notes': ''
            },
            {
                'Title': 'Example 2',
                'Percentage': '80.0000%',
                'Total Votes': '16',
                'URL': 'https://www.youtube.com/watch?v=dmVWvOC_2HU',
                'Notes': ''
            },
            {
                'Title': 'Example 3',
                'Percentage': '70.0000%',
                'Total Votes': '14',
                'URL': 'https://www.youtube.com/watch?v=dmVWvOC_2HU',
                'Notes': ''
            },
            { 'Title': '', 'Percentage': '', 'Total Votes': '', 'URL': '', 'Notes': '' },
            { 'Title': 'HONORABLE MENTIONS', 'Percentage': '', 'Total Votes': '', 'URL': '', 'Notes': '' },
            { 'Title': '', 'Percentage': '', 'Total Votes': '', 'URL': '', 'Notes': '' },
            {
                'Title': 'Example 4',
                'Percentage': '10.0000%',
                'Total Votes': '2',
                'URL': 'https://www.youtube.com/watch?v=dmVWvOC_2HU',
                'Notes': ''
            },
            { 'Title': '', 'Percentage': '', 'Total Votes': '', 'URL': '', 'Notes': '' },
            { 'Title': 'HISTORY', 'Percentage': '', 'Total Votes': '', 'URL': '', 'Notes': '' },
            { 'Title': '', 'Percentage': '', 'Total Votes': '', 'URL': '', 'Notes': '' },
            { 'Title': '1 year ago', 'Percentage': '', 'Total Votes': '', 'URL': '', 'Notes': '' },
            { 'Title': '', 'Percentage': '', 'Total Votes': '', 'URL': '', 'Notes': '' },
            {
                'Title': 'Example 5',
                'Percentage': '',
                'Total Votes': '',
                'URL': 'https://www.youtube.com/watch?v=dmVWvOC_2HU',
                'Notes': ''
            },
            { 'Title': '5 years ago', 'Percentage': '', 'Total Votes': '', 'URL': '', 'Notes': '' },
            { 'Title': '', 'Percentage': '', 'Total Votes': '', 'URL': '', 'Notes': '' },
            {
                'Title': 'Example 6',
                'Percentage': '',
                'Total Votes': '',
                'URL': 'https://www.youtube.com/watch?v=dmVWvOC_2HU',
                'Notes': ''
            },
            { 'Title': '10 years ago', 'Percentage': '', 'Total Votes': '', 'URL': '', 'Notes': '' },
            { 'Title': '', 'Percentage': '', 'Total Votes': '', 'URL': '', 'Notes': '' },
            {
                'Title': 'Example 7',
                'Percentage': '',
                'Total Votes': '',
                'URL': 'https://www.youtube.com/watch?v=dmVWvOC_2HU',
                'Notes': ''
            },
        ]

        grouped_records = parse_calculated_top_10_csv(records)
        self.assertEqual(3, len(grouped_records))

        self.assertIn('Top 10', grouped_records)
        self.assertIn('HONORABLE MENTIONS', grouped_records)
        self.assertIn('HISTORY', grouped_records)

        self.assertEqual(3, len(grouped_records['Top 10']))
        self.assertEqual('Example 1', grouped_records['Top 10'][0]['Title'])
        self.assertEqual('Example 2', grouped_records['Top 10'][1]['Title'])
        self.assertEqual('Example 3', grouped_records['Top 10'][2]['Title'])

        self.assertEqual(1, len(grouped_records['HONORABLE MENTIONS']))
        self.assertEqual('Example 4', grouped_records['HONORABLE MENTIONS'][0]['Title'])

        self.assertEqual(3, len(grouped_records['HISTORY']))
        self.assertIn('5 years ago', grouped_records['HISTORY'])
        self.assertIn('10 years ago', grouped_records['HISTORY'])

        self.assertEqual(1, len(grouped_records['HISTORY']['1 year ago']))
        self.assertEqual('Example 5', grouped_records['HISTORY']['1 year ago'][0]['Title'])
        self.assertEqual(1, len(grouped_records['HISTORY']['5 years ago']))
        self.assertEqual('Example 6', grouped_records['HISTORY']['5 years ago'][0]['Title'])
        self.assertEqual(1, len(grouped_records['HISTORY']['1 year ago']))
        self.assertEqual('Example 7', grouped_records['HISTORY']['10 years ago'][0]['Title'])

