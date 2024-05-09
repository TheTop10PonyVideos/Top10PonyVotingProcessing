from unittest import TestCase
from functions.similarity import get_string_similarity, get_duration_similarity, get_similarity_matrix, detect_cross_platform_uploads
from classes.voting import Video


class TestFunctionsSimilarity(TestCase):
    def test_get_duration_similarity(self):
        self.assertEqual(100, get_duration_similarity(96, 96))
        self.assertEqual(0, get_duration_similarity(96, 90))
        self.assertEqual(50, get_duration_similarity(96, 98.5))


    def test_get_string_similarity(self):
        self.assertEqual(100, get_string_similarity('Derpy', 'Derpy'))
        self.assertTrue(get_string_similarity('Derpy', 'Deryp') < 100)


    def test_get_similarity_matrix(self):
        table = {
            'Applejack': 'earth pony',
            'Pinkie Pie': 'earth pony',
            'Fluttershy': 'pegasus',
            'Rainbow Dash': 'pegasus',
            'Rarity': 'unicorn',
            'Twilight Sparkle': 'alicorn',
            'Derpy': 'pegasus',
        }

        similarity_matrix = get_similarity_matrix(table, get_string_similarity)
        self.assertEqual(7, len(similarity_matrix))
        self.assertEqual(7, len(similarity_matrix[0]))

        # All the matrix diagonals should be 100 (identical similarity), as
        # these represent comparing a value to itself.
        self.assertEqual(100, similarity_matrix[0][0])
        self.assertEqual(100, similarity_matrix[1][1])
        self.assertEqual(100, similarity_matrix[2][2])
        self.assertEqual(100, similarity_matrix[3][3])
        self.assertEqual(100, similarity_matrix[4][4])
        self.assertEqual(100, similarity_matrix[5][5])
        self.assertEqual(100, similarity_matrix[6][6])

        # (0, 1) should be the Applejack/Derpy comparison, since indices 0 and 1
        # correspond to those two keys when ordered lexicographically. Since
        # Applejack is an earth pony and Derpy is a pegasus, this should be an
        # imperfect match.
        self.assertTrue(similarity_matrix[0][1] < 100)

        # Applejack/Fluttershy (imperfect match)
        self.assertTrue(100, similarity_matrix[0][2] < 100)

        # (0, 3) should be the Applejack/Pinkie Pie comparison. They're both
        # earth ponies, so this should be a perfect match.
        self.assertEqual(100, similarity_matrix[0][3])

        # Applejack/Rainbow Dash (imperfect match)
        self.assertTrue(100, similarity_matrix[0][4] < 100)

        # Applejack/Rarity (imperfect match)
        self.assertTrue(100, similarity_matrix[0][5] < 100)

        # Applejack/Twilight Sparkle (imperfect match)
        self.assertTrue(100, similarity_matrix[0][6] < 100)

        # Fluttershy/Applejack (imperfect match)
        self.assertTrue(100, similarity_matrix[2][0] < 100)

        # Fluttershy/Derpy (perfect match)
        self.assertEqual(100, similarity_matrix[2][1])

        # Fluttershy/Rainbow Dash (perfect match)
        self.assertEqual(100, similarity_matrix[2][4])

        # Rarity/Twilight Sparkle (imperfect match)
        self.assertTrue(100, similarity_matrix[5][6] < 100)

        
    def test_detect_cross_platform_uploads(self):
        videos = {
            'https://example.com/1': Video(),
            'https://example.com/2': Video(),
            'https://example.com/3': Video(),
            'https://example.com/4': Video(),
            'https://example.com/5': Video(),
            'https://example.com/6': Video(),
            'https://example.com/7': Video(),
        }

        videos['https://example.com/1'].data = {
            'title': 'AAAAA',
            'uploader': 'EEEEE',
            'duration': 60,
        }
        videos['https://example.com/2'].data = {
            'title': 'AAAAA',
            'uploader': 'EEEEE',
            'duration': 60,
        }
        videos['https://example.com/3'].data = {
            'title': 'BBBBB',
            'uploader': 'FFFFF',
            'duration': 64,
        }
        videos['https://example.com/4'].data = {
            'title': 'BBBBB',
            'uploader': 'FFFFF',
            'duration': 120,
        }
        videos['https://example.com/5'].data = {
            'title': 'CCCCC',
            'uploader': 'GGGGG',
            'duration': 124.9,
        }
        videos['https://example.com/6'].data = {
            'title': 'DDDDD',
            'uploader': 'HHHHH',
            'duration': 9006,
        }
        
        similarity_table = detect_cross_platform_uploads(videos)
        self.assertEqual(4, len(similarity_table))

        # Only 4 videos should be in the similarity table:
        # * /1 is, because it is similar to /2 in title, uploader, and duration.
        # * /2 is, because it is similar to /1 in title, uploader, and duration.
        # * /3 is, because it is similar to /4 in title and uploader.
        # * /4 is, because it is similar to /3 in title and uploader.
        # * /5 isn't, because it's only similar to /4 in duration, which isn't
        #   enough for the cross-platform check.
        # * /6 isn't, because it's not similar in any properties.
        # * /7 isn't, because it has no data.
        self.assertIn('https://example.com/1', similarity_table)
        self.assertIn('https://example.com/2', similarity_table)
        self.assertIn('https://example.com/3', similarity_table)
        self.assertIn('https://example.com/4', similarity_table)
        self.assertNotIn('https://example.com/5', similarity_table)
        self.assertNotIn('https://example.com/6', similarity_table)
        self.assertNotIn('https://example.com/7', similarity_table)
        
        self.assertEqual(1, len(similarity_table['https://example.com/1']))
        self.assertIn('https://example.com/2', similarity_table['https://example.com/1'])

        self.assertEqual(1, len(similarity_table['https://example.com/2']))
        self.assertIn('https://example.com/1', similarity_table['https://example.com/2'])

        self.assertEqual(1, len(similarity_table['https://example.com/3']))
        self.assertIn('https://example.com/4', similarity_table['https://example.com/3'])

        self.assertEqual(1, len(similarity_table['https://example.com/4']))
        self.assertIn('https://example.com/3', similarity_table['https://example.com/4'])

        self.assertEqual(['title', 'uploader', 'duration'], similarity_table['https://example.com/1']['https://example.com/2'])


    def test_detect_cross_platform_uploads_normalization(self):
        # Test normalization of YouTube URLs. Here, there are 2 YouTube URLs for
        # Tridashie's "Nightmare Virus" which should normalize to the same URL.
        videos = {
            'https://youtu.be/9RT4lfvVFhA': Video(),
            'https://www.youtube.com/watch?v=9RT4lfvVFhA': Video(),
            'https://www.youtube.com/live/Q8k4UTf8jiI': Video(),
            'https://www.bilibili.com/video/ABCDEFGHIJKL/': Video(),
            'https://pony.tube/w/abcdefghijklmnopqrstuv': Video(),
        }

        videos['https://youtu.be/9RT4lfvVFhA'].data = {
            'title': 'Nightmare Virus',
            'uploader': 'Tridashie',
            'duration': 99,
        }
        videos['https://www.youtube.com/watch?v=9RT4lfvVFhA'].data = {
            'title': 'Nightmare Virus',
            'uploader': 'Tridashie',
            'duration': 99,
        }
        videos['https://www.youtube.com/live/Q8k4UTf8jiI'].data = {
            'title': 'Stream Ends When We Get One Wrong - PonyGuessr Permadeath #3',
            'uploader': 'LittleshyFiM',
            'duration': 500,
        }
        videos['https://www.bilibili.com/video/ABCDEFGHIJKL/'].data = {
            'title': 'Nightmare Virus',
            'uploader': 'Tridashie',
            'duration': 99,
        }
        videos['https://pony.tube/w/abcdefghijklmnopqrstuv'].data = {
            'title': 'Stream Ends When We Get One Wrong - PonyGuessr Permadeath #3',
            'uploader': 'LittleshyFiM',
            'duration': 500,
        }

        similarity_table = detect_cross_platform_uploads(videos)

        # Although there are 5 URLs, the similarity table should have 4 entries
        # because two normalize to the same YouTube URL.
        self.assertEqual(4, len(similarity_table))

        self.assertIn('https://www.youtube.com/watch?v=9RT4lfvVFhA', similarity_table)
        self.assertIn('https://www.youtube.com/watch?v=Q8k4UTf8jiI', similarity_table)
        self.assertIn('https://www.bilibili.com/video/ABCDEFGHIJKL/', similarity_table)
        self.assertIn('https://pony.tube/w/abcdefghijklmnopqrstuv', similarity_table)

        # Although this URL was in the list, it should have been normalized to
        # "https://www.youtube.com/watch?v=9RT4lfvVFhA" - thus, it doesn't
        # appear in the similarity table.
        self.assertNotIn('https://youtu.be/9RT4lfvVFhA', similarity_table)

        # Similarly, this URL should have been normalized to
        # "https://www.youtube.com/watch?v=Q8k4UTf8jiI" and thus also doesn't
        # appear.
        self.assertNotIn('https://www.youtube.com/live/Q8k4UTf8jiI', similarity_table)
