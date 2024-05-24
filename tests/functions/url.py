from unittest import TestCase
from functions.url import is_youtube_url, normalize_youtube_url


class TestFunctionsUrl(TestCase):
    def test_is_youtube_url(self):
        self.assertTrue(is_youtube_url("https://www.youtube.com/watch?v=9RT4lfvVFhA"))
        self.assertTrue(is_youtube_url("https://www.youtube.com/live/Q8k4UTf8jiI"))
        self.assertTrue(is_youtube_url("https://youtu.be/9RT4lfvVFhA"))
        self.assertTrue(is_youtube_url("https://youtube.com/watch?v=9RT4lfvVFhA"))
        self.assertTrue(is_youtube_url("https://m.youtube.com/watch?v=9RT4lfvVFhA"))
        self.assertFalse(is_youtube_url("https://www.bilibili.com/video/BV1HC411H7Po/"))
        self.assertFalse(is_youtube_url("https://pony.tube/w/bYSyWpjg6r6zo68o1imK5t"))

    def test_normalize_youtube_url(self):
        # These should all normalize to the same YouTube URL
        normalized_url = "https://www.youtube.com/watch?v=Q8k4UTf8jiI"

        self.assertEqual(
            normalized_url,
            normalize_youtube_url("https://www.youtube.com/watch?v=Q8k4UTf8jiI"),
        )
        self.assertEqual(
            normalized_url,
            normalize_youtube_url("https://www.youtube.com/live/Q8k4UTf8jiI"),
        )
        self.assertEqual(
            normalized_url, normalize_youtube_url("https://youtu.be/Q8k4UTf8jiI")
        )
        self.assertEqual(
            normalized_url,
            normalize_youtube_url(
                "https://www.youtube.com/watch?app=desktop&v=Q8k4UTf8jiI"
            ),
        )

        # Non-YouTube links should raise a ValueError
        with self.assertRaises(ValueError):
            normalize_youtube_url("https://www.bilibili.com/video/BV1HC411H7Po/")

        with self.assertRaises(ValueError):
            normalize_youtube_url("https://pony.tube/w/bYSyWpjg6r6zo68o1imK5t")
