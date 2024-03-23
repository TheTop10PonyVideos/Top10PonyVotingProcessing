from unittest import TestCase
from functions.ballot_rules import check_duplicates, check_blacklisted_ballots, check_ballot_upload_dates, check_ballot_video_durations, check_fuzzy, check_ballot_uploader_occurrences, check_ballot_uploader_diversity
from classes.voting import Ballot, Vote, Video


class TestFunctionsBallotRules(TestCase):
    def test_check_duplicates(self):
        ballots = [
            # No duplicates
            Ballot(
                '4/1/2024 9:00:00',
                [
                    Vote('https://example.com/1'),
                    Vote('https://example.com/2'),
                    Vote('https://example.com/3'),
                    Vote('https://example.com/4'),
                    Vote('https://example.com/5'),
                ]
            ),
            # One duplicate
            Ballot(
                '4/2/2024 9:00:00',
                [
                    Vote('https://example.com/1'),
                    Vote('https://example.com/2'),
                    Vote('https://example.com/1'),
                    Vote('https://example.com/3'),
                    Vote('https://example.com/4'),
                ]
            ),
            # 3 duplicates
            Ballot(
                '4/3/2024 9:00:00',
                [
                    Vote('https://example.com/1'),
                    Vote('https://example.com/2'),
                    Vote('https://example.com/1'),
                    Vote('https://example.com/1'),
                    Vote('https://example.com/2'),
                ]
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
        self.assertTrue(ballots[1].votes[2].annotations.has('DUPLICATE VIDEO'))
        self.assertTrue(ballots[1].votes[3].annotations.has_none())
        self.assertTrue(ballots[1].votes[4].annotations.has_none())

        self.assertTrue(ballots[2].votes[0].annotations.has_none())
        self.assertTrue(ballots[2].votes[1].annotations.has_none())
        self.assertTrue(ballots[2].votes[2].annotations.has('DUPLICATE VIDEO'))
        self.assertTrue(ballots[2].votes[3].annotations.has('DUPLICATE VIDEO'))
        self.assertTrue(ballots[2].votes[3].annotations.has('DUPLICATE VIDEO'))


    def test_check_fuzzy(self):
        ballots = [
            Ballot(
                '4/1/2024 9:00:00',
                [
                    Vote('https://example.com/1'),
                    Vote('https://example.com/2'),
                    Vote('https://example.com/3'),
                    Vote('https://example.com/4'),
                    Vote('https://example.com/5'),
                ]
            ),
            Ballot(
                '4/2/2024 9:00:00',
                [
                    Vote('https://example.com/6'),
                    Vote('https://example.com/7'),
                    Vote('https://example.com/8'),
                    Vote('https://example.com/9'),
                    Vote('https://example.com/10'),
                ]
            ),
            Ballot(
                '4/3/2024 9:00:00',
                [
                    Vote('https://example.com/11'),
                    Vote('https://example.com/12'),
                    Vote('https://example.com/13'),
                    Vote('https://example.com/14'),
                    Vote('https://example.com/15'),
                ]
            ),
        ]

        videos = {
            'https://example.com/1': Video(
                {
                    'title': 'AAAAA',
                    'uploader': 'AAAAA',
                    'duration': 60,
                }
            ),
            'https://example.com/2': Video(
                {
                    'title': 'BBBBB',
                    'uploader': 'BBBBB',
                    'duration': 120,
                }
            ),
            'https://example.com/3': Video(
                {
                    'title': 'BBBBB',
                    'uploader': 'CCCCC',
                    'duration': 180,
                }
            ),
            'https://example.com/4': Video(
                {
                    'title': 'CCCCC',
                    'uploader': 'DDDDD',
                    'duration': 240,
                }
            ),
            'https://example.com/5': Video(
                {
                    'title': 'DDDDD',
                    'uploader': 'DDDDD',
                    'duration': 300,
                }
            ),
            'https://example.com/6': Video(
                {
                    'title': 'AAAAA',
                    'uploader': 'AAAAA',
                    'duration': 60,
                }
            ),
            'https://example.com/7': Video(
                {
                    'title': 'BBBBB',
                    'uploader': 'BBBBB',
                    'duration': 120,
                }
            ),
            'https://example.com/8': Video(
                {
                    'title': 'CCCCC',
                    'uploader': 'CCCCC',
                    'duration': 180,
                }
            ),
            'https://example.com/9': Video(
                {
                    'title': 'DDDDD',
                    'uploader': 'DDDDD',
                    'duration': 240,
                }
            ),
            'https://example.com/10': Video(
                {
                    'title': 'EEEEE',
                    'uploader': 'EEEEE',
                    'duration': 300,
                }
            ),
            'https://example.com/11': Video(
                {
                    'title': 'AAAAA',
                    'uploader': 'AAAAA',
                    'duration': 60,
                }
            ),
            'https://example.com/12': Video(
                {
                    'title': 'AAAAA',
                    'uploader': 'AAAAA',
                    'duration': 60,
                }
            ),
            'https://example.com/13': Video(
                {
                    'title': 'AAAAA',
                    'uploader': 'AAAAA',
                    'duration': 60,
                }
            ),
            'https://example.com/14': Video(
                {
                    'title': 'AAAAA',
                    'uploader': 'AAAAA',
                    'duration': 60,
                }
            ),
            'https://example.com/15': Video(
                {
                    'title': 'AAAAA',
                    'uploader': 'AAAAA',
                    'duration': 60,
                }
            ),
        }

        check_fuzzy(ballots, videos, 100)

        self.assertTrue(ballots[0].votes[0].annotations.has_none())
        self.assertEqual(1, ballots[0].votes[1].annotations.count())
        self.assertEqual(1, ballots[0].votes[2].annotations.count())
        self.assertEqual(1, ballots[0].votes[3].annotations.count())
        self.assertEqual(1, ballots[0].votes[4].annotations.count())
        self.assertTrue(ballots[0].votes[1].annotations.has('SIMILARITY DETECTED IN TITLE'))
        self.assertTrue(ballots[0].votes[2].annotations.has('SIMILARITY DETECTED IN TITLE'))
        self.assertTrue(ballots[0].votes[3].annotations.has('SIMILARITY DETECTED IN UPLOADER'))
        self.assertTrue(ballots[0].votes[4].annotations.has('SIMILARITY DETECTED IN UPLOADER'))


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
        self.assertTrue(ballots[2].votes[0].annotations.has('SIMILARITY DETECTED IN TITLE AND UPLOADER AND DURATION'))
        self.assertTrue(ballots[2].votes[1].annotations.has('SIMILARITY DETECTED IN TITLE AND UPLOADER AND DURATION'))
        self.assertTrue(ballots[2].votes[2].annotations.has('SIMILARITY DETECTED IN TITLE AND UPLOADER AND DURATION'))
        self.assertTrue(ballots[2].votes[3].annotations.has('SIMILARITY DETECTED IN TITLE AND UPLOADER AND DURATION'))
        self.assertTrue(ballots[2].votes[4].annotations.has('SIMILARITY DETECTED IN TITLE AND UPLOADER AND DURATION'))


    def test_check_ballot_uploader_occurrences(self):
        ballots = [
            # Too many votes for one creator
            Ballot(
                '4/1/2024 9:00:00',
                [
                    Vote('https://example.com/1'),
                    Vote('https://example.com/2'),
                    Vote('https://example.com/3'),
                    Vote('https://example.com/4'),
                    Vote('https://example.com/5'),
                    Vote('https://example.com/6'),
                    Vote('https://example.com/7'),
                    Vote('https://example.com/8'),
                    Vote('https://example.com/9'),
                    Vote('https://example.com/10'),
                ]
            ),
            # Acceptable
            Ballot(
                '4/2/2024 9:00:00',
                [
                    Vote('https://example.com/11'),
                    Vote('https://example.com/12'),
                    Vote('https://example.com/13'),
                    Vote('https://example.com/14'),
                    Vote('https://example.com/15'),
                ]
            ),
        ]

        videos = {
            'https://example.com/1': Video({'uploader': 'AAAAA'}),
            'https://example.com/2': Video({'uploader': 'AAAAA'}),
            'https://example.com/3': Video({'uploader': 'AAAAA'}),
            'https://example.com/4': Video({'uploader': 'AAAAA'}),
            'https://example.com/5': Video({'uploader': 'BBBBB'}),
            'https://example.com/6': Video({'uploader': 'BBBBB'}),
            'https://example.com/7': Video({'uploader': 'BBBBB'}),
            'https://example.com/8': Video({'uploader': 'CCCCC'}),
            'https://example.com/9': Video({'uploader': 'CCCCC'}),
            'https://example.com/10': Video({'uploader': 'DDDDD'}),
            'https://example.com/11': Video({'uploader': 'AAAAA'}),
            'https://example.com/12': Video({'uploader': 'AAAAA'}),
            'https://example.com/13': Video({'uploader': 'BBBBB'}),
            'https://example.com/14': Video({'uploader': 'BBBBB'}),
            'https://example.com/15': Video({'uploader': 'CCCCC'}),
        }

        check_ballot_uploader_occurrences(ballots, videos)
        self.assertTrue(ballots[0].votes[0].annotations.has('DUPLICATE CREATOR'))
        self.assertTrue(ballots[0].votes[1].annotations.has('DUPLICATE CREATOR'))
        self.assertTrue(ballots[0].votes[2].annotations.has('DUPLICATE CREATOR'))
        self.assertTrue(ballots[0].votes[3].annotations.has('DUPLICATE CREATOR'))
        self.assertTrue(ballots[0].votes[4].annotations.has('DUPLICATE CREATOR'))
        self.assertTrue(ballots[0].votes[5].annotations.has('DUPLICATE CREATOR'))
        self.assertTrue(ballots[0].votes[6].annotations.has('DUPLICATE CREATOR'))
        self.assertTrue(ballots[0].votes[7].annotations.has_none())
        self.assertTrue(ballots[0].votes[8].annotations.has_none())
        self.assertTrue(ballots[0].votes[9].annotations.has_none())
        self.assertTrue(ballots[1].votes[0].annotations.has_none())
        self.assertTrue(ballots[1].votes[1].annotations.has_none())
        self.assertTrue(ballots[1].votes[2].annotations.has_none())
        self.assertTrue(ballots[1].votes[3].annotations.has_none())
        self.assertTrue(ballots[1].votes[4].annotations.has_none())
        

    def test_check_ballot_uploader_diversity(self):
        ballots = [
            # All votes for the same uploader
            Ballot(
                '4/1/2024 9:00:00',
                [
                    Vote('https://example.com/1'),
                    Vote('https://example.com/2'),
                    Vote('https://example.com/3'),
                    Vote('https://example.com/4'),
                    Vote('https://example.com/5'),
                    Vote('https://example.com/6'),
                    Vote('https://example.com/7'),
                    Vote('https://example.com/8'),
                    Vote('https://example.com/9'),
                    Vote('https://example.com/10'),
                ]
            ),
            # Sufficiently diverse
            Ballot(
                '4/2/2024 9:00:00',
                [
                    Vote('https://example.com/11'),
                    Vote('https://example.com/12'),
                    Vote('https://example.com/13'),
                    Vote('https://example.com/14'),
                    Vote('https://example.com/15'),
                ]
            ),
        ]

        videos = {
            'https://example.com/1': Video({'uploader': 'AAAAA'}),
            'https://example.com/2': Video({'uploader': 'AAAAA'}),
            'https://example.com/3': Video({'uploader': 'AAAAA'}),
            'https://example.com/4': Video({'uploader': 'AAAAA'}),
            'https://example.com/5': Video({'uploader': 'AAAAA'}),
            'https://example.com/6': Video({'uploader': 'AAAAA'}),
            'https://example.com/7': Video({'uploader': 'AAAAA'}),
            'https://example.com/8': Video({'uploader': 'AAAAA'}),
            'https://example.com/9': Video({'uploader': 'AAAAA'}),
            'https://example.com/10': Video({'uploader': 'AAAAA'}),
            'https://example.com/11': Video({'uploader': 'AAAAA'}),
            'https://example.com/12': Video({'uploader': 'BBBBB'}),
            'https://example.com/13': Video({'uploader': 'CCCCC'}),
            'https://example.com/14': Video({'uploader': 'DDDDD'}),
            'https://example.com/15': Video({'uploader': 'EEEEE'}),
        }

        check_ballot_uploader_diversity(ballots, videos)

        self.assertTrue(ballots[0].votes[0].annotations.has('5 CHANNEL RULE'))
        self.assertTrue(ballots[0].votes[1].annotations.has('5 CHANNEL RULE'))
        self.assertTrue(ballots[0].votes[2].annotations.has('5 CHANNEL RULE'))
        self.assertTrue(ballots[0].votes[3].annotations.has('5 CHANNEL RULE'))
        self.assertTrue(ballots[0].votes[4].annotations.has('5 CHANNEL RULE'))
        self.assertTrue(ballots[0].votes[5].annotations.has('5 CHANNEL RULE'))
        self.assertTrue(ballots[0].votes[6].annotations.has('5 CHANNEL RULE'))
        self.assertTrue(ballots[0].votes[7].annotations.has('5 CHANNEL RULE'))
        self.assertTrue(ballots[0].votes[8].annotations.has('5 CHANNEL RULE'))
        self.assertTrue(ballots[0].votes[9].annotations.has('5 CHANNEL RULE'))
        self.assertTrue(ballots[1].votes[0].annotations.has_none())
        self.assertTrue(ballots[1].votes[1].annotations.has_none())
        self.assertTrue(ballots[1].votes[2].annotations.has_none())
        self.assertTrue(ballots[1].votes[3].annotations.has_none())
        self.assertTrue(ballots[1].votes[4].annotations.has_none())

        
    def test_other_ballot_checks(self):
        ballots = [
            Ballot(
                '4/1/2024 9:00:00',
                [
                    Vote('https://example.com/1'),
                    Vote('https://example.com/2'),
                ]
            ),
            Ballot(
                '4/2/2024 9:00:00',
                [
                    Vote('https://example.com/3'),
                    Vote('https://example.com/4'),
                ]
            ),
        ]

        videos = {
            'https://example.com/1': Video({'title': 'Example Video 1'}),
            'https://example.com/2': Video({'title': 'Example Video 2'}),
            'https://example.com/3': Video({'title': 'Example Video 3'}),
            'https://example.com/4': Video({'title': 'Example Video 4'}),
        }

        videos['https://example.com/1'].annotations.add('BLACKLISTED')
        videos['https://example.com/1'].annotations.add('VIDEO TOO OLD')
        videos['https://example.com/1'].annotations.add('VIDEO TOO SHORT')
        videos['https://example.com/2'].annotations.add('BLACKLISTED')
        videos['https://example.com/2'].annotations.add('VIDEO MAYBE TOO SHORT')
        videos['https://example.com/3'].annotations.add('VIDEO TOO NEW')

        check_blacklisted_ballots(ballots, videos)
        check_ballot_upload_dates(ballots, videos)
        check_ballot_video_durations(ballots, videos)

        self.assertTrue(ballots[0].votes[0].annotations.has('BLACKLISTED'))
        self.assertTrue(ballots[0].votes[0].annotations.has('VIDEO TOO OLD'))
        self.assertTrue(ballots[0].votes[0].annotations.has('VIDEO TOO SHORT'))
        self.assertTrue(ballots[0].votes[1].annotations.has('BLACKLISTED'))
        self.assertTrue(ballots[0].votes[1].annotations.has('VIDEO MAYBE TOO SHORT'))
        self.assertTrue(ballots[1].votes[0].annotations.has('VIDEO TOO NEW'))
        self.assertTrue(ballots[1].votes[1].annotations.has_none())
