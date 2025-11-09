import pytest
from unittest import TestCase
from functions.url import is_youtube_url, normalize_youtube_url, normalize_derpibooru_url


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
            normalize_youtube_url("https://www.youtube.com/watch?v=Q8k4UTf8jiI")[0],
        )
        self.assertEqual(
            normalized_url,
            normalize_youtube_url("https://www.youtube.com/live/Q8k4UTf8jiI")[0],
        )
        self.assertEqual(
            normalized_url, normalize_youtube_url("https://youtu.be/Q8k4UTf8jiI")[0]
        )
        self.assertEqual(
            normalized_url,
            normalize_youtube_url(
                "https://www.youtube.com/watch/?app=desktop&v=Q8k4UTf8jiI"
            )[0],
        )
        self.assertEqual(
            normalized_url,
            normalize_youtube_url("https://www.youtube.com/shorts/Q8k4UTf8jiI/")[0]
        )

        self.assertEqual(
            "https://www.youtube.com/watch?v=watch000000",
            normalize_youtube_url("https://youtu.be/watch000000?v=Q8k4UTf8jiI")[0]
        )

        # Malformed links should raise errors
        with self.assertRaises(ValueError):
            normalize_youtube_url("https://www.youtube.com/watch?vQ8k4UTf8jiI")

        with self.assertRaises(ValueError):
            normalize_youtube_url("https://www.youtube.com/shorts?v=Q8k4UTf8jiI")

        # Non-YouTube links should raise a ValueError
        with self.assertRaises(ValueError):
            normalize_youtube_url("https://www.bilibili.com/video/BV1HC411H7Po/")

        with self.assertRaises(ValueError):
            normalize_youtube_url("https://pony.tube/w/bYSyWpjg6r6zo68o1imK5t")


# pytest tests
def test_normalize_derpibooru_url():
    assert normalize_derpibooru_url("https://derpibooru.org/images/1130155?sort%5B%5D=452&sort%5B%5D=1130155&sd=desc&sf=score&q=derpy%2Cmuffin") == "https://derpibooru.org/images/1130155"

    assert normalize_derpibooru_url("https://derpibooru.org/images/1130155") == "https://derpibooru.org/images/1130155"

    with pytest.raises(ValueError):
        normalize_derpibooru_url("https://derpibooru.org/tags/derpy+hooves")

    with pytest.raises(ValueError):
        assert normalize_derpibooru_url("https://derpibooru.org")
