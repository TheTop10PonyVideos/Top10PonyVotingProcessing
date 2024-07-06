from unittest import TestCase
from datetime import datetime
from functions.top_10_calc import process_shifted_voting_data, calc_ranked_records, get_history

class TestFunctionsTop10Calc(TestCase):
    def test_process_shifted_voting_data(self):
        rows = [
            ['Timestamp', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
            ['4/1/2024 0:11:59', '',  'Title A', '', 'Title B', '', 'Title C', '','Title D', '', 'Title E', '', 'Title F', '', 'Title G', '', 'Title H', '', 'Title I', '', 'Title J', ''],
            ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
            ['4/2/2024 0:11:59', '',  'Title K', '', 'Title L', '', 'Title M', '','Title N', '', 'Title O', '', 'Title P', '', 'Title Q', '', 'Title R', '', 'Title S', ''],
        ]

        data_rows = process_shifted_voting_data(rows)

        self.assertEqual(2, len(data_rows))
        self.assertEqual(10, len(data_rows[0]))
        self.assertEqual(9, len(data_rows[1]))
        self.assertEqual('Title A', data_rows[0][0])
        self.assertEqual('Title B', data_rows[0][1])
        self.assertEqual('Title C', data_rows[0][2])
        self.assertEqual('Title J', data_rows[0][9])
        self.assertEqual('Title K', data_rows[1][0])
        self.assertEqual('Title L', data_rows[1][1])
        self.assertEqual('Title M', data_rows[1][2])
        self.assertEqual('Title S', data_rows[1][8])


    def test_calc_ranked_records(self):
        title_rows = [
            ['Title A',  'Title B', 'Title C', 'Title D', 'Title E'],
            ['Title A',  'Title B', 'Title C', 'Title D', 'Title E'],
            ['Title A',  'Title B', 'Title C', 'Title D', 'Title K'],
            ['Title A',  'Title B', 'Title C', 'Title M', 'Title N'],
            ['Title A',  'Title B', 'Title O', 'Title P', 'Title Q'],
            ['Title A',  'Title B', 'Title R', 'Title S', 'Title T'],
            ['Title A',  'Title B', 'Title U', 'Title V', 'Title W'],
            ['Title A',  'Title X', 'Title Y', 'Title Z', 'Title 0'],
            ['Title A',  'Title 1', 'Title 2', 'Title 3'],
            ['Title F',  'Title 4', 'Title 5', 'Title 6', 'Title 7'],
        ]

        titles_to_urls = {
            'Title A': 'https://example.com/Title_A',
            'Title B': 'https://example.com/Title_B',
            'Title C': 'https://example.com/Title_C',
            'Title D': 'https://example.com/Title_D',
            'Title E': 'https://example.com/Title_E',
            'Title K': 'https://example.com',
            'Title M': 'https://example.com',
            'Title N': 'https://example.com',
            'Title O': 'https://example.com',
            'Title P': 'https://example.com',
            'Title Q': 'https://example.com',
            'Title R': 'https://example.com',
            'Title S': 'https://example.com',
            'Title T': 'https://example.com',
            'Title U': 'https://example.com',
            'Title V': 'https://example.com',
            'Title W': 'https://example.com',
            'Title X': 'https://example.com',
            'Title Y': 'https://example.com',
            'Title Z': 'https://example.com',
            'Title 0': 'https://example.com',
            'Title 1': 'https://example.com',
            'Title 2': 'https://example.com',
            'Title 3': 'https://example.com',
            'Title F': 'https://example.com',
            'Title 4': 'https://example.com',
            'Title 5': 'https://example.com',
            'Title 6': 'https://example.com',
            'Title 7': 'https://example.com',
        }

        records = calc_ranked_records(title_rows, titles_to_urls)
        self.assertEqual(29, len(records))
        self.assertEqual('Title A', records[0]['Title'])
        self.assertEqual('90.0000%', records[0]['Percentage'])
        self.assertEqual(9, records[0]['Total Votes'])
        self.assertEqual('https://example.com/Title_A', records[0]['URL'])
        self.assertEqual('Title B', records[1]['Title'])
        self.assertEqual('70.0000%', records[1]['Percentage'])
        self.assertEqual(7, records[1]['Total Votes'])
        self.assertEqual('https://example.com/Title_B', records[1]['URL'])
        self.assertEqual('Title C', records[2]['Title'])
        self.assertEqual('40.0000%', records[2]['Percentage'])
        self.assertEqual(4, records[2]['Total Votes'])
        self.assertEqual('https://example.com/Title_C', records[2]['URL'])
        self.assertEqual('Title D', records[3]['Title'])
        self.assertEqual('30.0000%', records[3]['Percentage'])
        self.assertEqual(3, records[3]['Total Votes'])
        self.assertEqual('https://example.com/Title_D', records[3]['URL'])
        self.assertEqual('Title E', records[4]['Title'])
        self.assertEqual('20.0000%', records[4]['Percentage'])
        self.assertEqual(2, records[4]['Total Votes'])
        self.assertEqual('https://example.com/Title_E', records[4]['URL'])

        # Test tie-breaking. A should be first; B and C should tie for 2nd (and
        # thus be 2nd and 3rd after a tie-break); D, E, and F should tie and be
        # 4th, 5th, and 6th; G, H, I, J, K, L should tie and be 7th to 12th.
        title_rows = [
            ['A',  'B', 'C', 'E', 'H'],
            ['A',  'B', 'C', 'E', 'I'],
            ['A',  'B', 'C', 'F', 'J'],
            ['A',  'B', 'D', 'F', 'K'],
            ['A',  'C', 'D', 'G', 'L'],
        ]

        titles_to_urls = {
            'A': 'https://example.com/A',
            'B': 'https://example.com/B',
            'C': 'https://example.com/C',
            'D': 'https://example.com/D',
            'E': 'https://example.com/E',
            'F': 'https://example.com/F',
            'G': 'https://example.com/G',
            'H': 'https://example.com/H',
            'I': 'https://example.com/I',
            'J': 'https://example.com/J',
            'K': 'https://example.com/K',
            'L': 'https://example.com/L',
        }

        records = calc_ranked_records(title_rows, titles_to_urls)

        self.assertEqual('A', records[0]['Title'])
        self.assertTrue(records[1]['Title'] in ('B', 'C'))
        self.assertTrue(records[2]['Title'] in ('B', 'C'))
        self.assertTrue(records[3]['Title'] in ('D', 'E', 'F'))
        self.assertTrue(records[4]['Title'] in ('D', 'E', 'F'))
        self.assertTrue(records[5]['Title'] in ('D', 'E', 'F'))
        self.assertTrue(records[6]['Title'] in ('G', 'H', 'I', 'J', 'K', 'L'))
        self.assertTrue(records[7]['Title'] in ('G', 'H', 'I', 'J', 'K', 'L'))
        self.assertTrue(records[8]['Title'] in ('G', 'H', 'I', 'J', 'K', 'L'))
        self.assertTrue(records[9]['Title'] in ('G', 'H', 'I', 'J', 'K', 'L'))
        self.assertTrue(records[10]['Title'] in ('G', 'H', 'I', 'J', 'K', 'L'))
        self.assertTrue(records[11]['Title'] in ('G', 'H', 'I', 'J', 'K', 'L'))

        self.assertEqual('', records[0]['Notes'])
        self.assertEqual('Tie broken by random choice', records[1]['Notes'])
        self.assertEqual('Tie broken by random choice', records[2]['Notes'])
        self.assertEqual('Tie broken by random choice', records[3]['Notes'])
        self.assertEqual('Tie broken by random choice', records[4]['Notes'])
        self.assertEqual('Tie broken by random choice', records[5]['Notes'])
        self.assertEqual('Tie broken by random choice', records[6]['Notes'])
        self.assertEqual('Tie broken by random choice', records[7]['Notes'])
        self.assertEqual('Tie broken by random choice', records[8]['Notes'])
        self.assertEqual('Tie broken by random choice', records[9]['Notes'])
        self.assertEqual('Tie broken by random choice', records[10]['Notes'])
        self.assertEqual('Tie broken by random choice', records[11]['Notes'])

    def test_get_history(self):
        from_date = datetime(2024, 4, 1)

        archive_records = [
            {'year': 2011, 'month': 1, 'title': 'Example 1'},
            {'year': 2011, 'month': 2, 'title': 'Example 2'},
            {'year': 2011, 'month': 3, 'title': 'Example 3'},
            {'year': 2011, 'month': 4, 'title': 'Example 4'},
            {'year': 2011, 'month': 5, 'title': 'Example 5'},
            {'year': 2011, 'month': 6, 'title': 'Example 6'},
            {'year': 2011, 'month': 7, 'title': 'Example 7'},
            {'year': 2011, 'month': 8, 'title': 'Example 8'},
            {'year': 2011, 'month': 9, 'title': 'Example 9'},
            {'year': 2011, 'month': 10, 'title': 'Example 10'},
            {'year': 2011, 'month': 11, 'title': 'Example 11'},
            {'year': 2011, 'month': 12, 'title': 'Example 12'},
            {'year': 2012, 'month': 1, 'title': 'Example 13'},
            {'year': 2012, 'month': 4, 'title': 'Example 14'},
            {'year': 2012, 'month': 12, 'title': 'Example 15'},
            {'year': 2013, 'month': 1, 'title': 'Example 16'},
            {'year': 2013, 'month': 4, 'title': 'Example 17'},
            {'year': 2013, 'month': 12, 'title': 'Example 18'},
            {'year': 2014, 'month': 1, 'title': 'Example 19'},
            {'year': 2014, 'month': 3, 'title': 'Example 20'},
            {'year': 2014, 'month': 4, 'day': 1, 'title': 'Example 21'},
            {'year': 2014, 'month': 4, 'day': 4, 'title': 'Example 22'},
            {'year': 2014, 'month': 4, 'day': 30, 'title': 'Example 23'},
            {'year': 2014, 'month': 5, 'title': 'Example 24'},
            {'year': 2014, 'month': 12, 'title': 'Example 25'},
            {'year': 2017, 'month': 4, 'title': 'Example 26'},
            {'year': 2017, 'month': 4, 'title': 'Example 27'},
            {'year': 2019, 'month': 4, 'day': 1, 'title': 'Example 28'},
            {'year': 2019, 'month': 4, 'day': 1, 'title': 'Example 29'},
            {'year': 2020, 'month': 4, 'title': 'Example 30'},
            {'year': 2021, 'month': 4, 'title': 'Example 31'},
            {'year': 2022, 'month': 4, 'title': 'Example 32'},
            {'year': 2023, 'month': 4, 'title': 'Example 33'},
            {'year': 2024, 'month': 4, 'title': 'Example 34'},
        ]

        history = get_history(archive_records, from_date, [1, 5, 10])
        self.assertEqual(3, len(history))
        self.assertIn(1, history)
        self.assertIn(5, history)
        self.assertIn(10, history)

        self.assertEqual(1, len(history[1]))
        self.assertEqual(2, len(history[5]))
        self.assertEqual(3, len(history[10]))

        self.assertEqual('Example 33', history[1][0]['title'])
        self.assertEqual('Example 28', history[5][0]['title'])
        self.assertEqual('Example 29', history[5][1]['title'])
        self.assertEqual('Example 21', history[10][0]['title'])
        self.assertEqual('Example 22', history[10][1]['title'])
        self.assertEqual('Example 23', history[10][2]['title'])
