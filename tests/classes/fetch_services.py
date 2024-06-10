from unittest import TestCase
from classes.fetch_services import YouTubeFetchService


class TestFetchServices(TestCase):
    def test_YouTubeFetchService(self):
        service = YouTubeFetchService("API_KEY", False)

        # Regular YouTube URL
        url = "https://www.youtube.com/watch?v=9RT4lfvVFhA"
        self.assertTrue(service.can_fetch(url))
        self.assertEqual("9RT4lfvVFhA", service.extract_video_id(url))

        # Shortened YouTube URL
        url = "https://youtu.be/9RT4lfvVFhA"
        self.assertTrue(service.can_fetch(url))
        self.assertEqual("9RT4lfvVFhA", service.extract_video_id(url))

        # Shortened YouTube URL with social tracking identifier
        url = "https://youtu.be/9RT4lfvVFhA?si=WXC57zYboHEsKd-C"
        self.assertTrue(service.can_fetch(url))
        self.assertEqual("9RT4lfvVFhA", service.extract_video_id(url))

        # Livestream URL
        url = "https://www.youtube.com/live/Q8k4UTf8jiI"
        self.assertTrue(service.can_fetch(url))
        self.assertEqual("Q8k4UTf8jiI", service.extract_video_id(url))

        # Livestream URL with social tracking identifier
        url = "https://www.youtube.com/live/Q8k4UTf8jiI?si=Ohm26zie1Gp07sBV"
        self.assertTrue(service.can_fetch(url))
        self.assertEqual("Q8k4UTf8jiI", service.extract_video_id(url))

        # Regular YouTube URL with `v=` as the second query parameter
        url = "https://www.youtube.com/watch?app=desktop&v=KeXztnxcHbc"
        self.assertTrue(service.can_fetch(url))
        self.assertEqual("KeXztnxcHbc", service.extract_video_id(url))

        # Non-YouTube URL
        url = "https://pony.tube/w/2FCj5YvmdHy8AC2hkEbc9i"
        self.assertFalse(service.can_fetch(url))
        self.assertEqual(None, service.extract_video_id(url))
