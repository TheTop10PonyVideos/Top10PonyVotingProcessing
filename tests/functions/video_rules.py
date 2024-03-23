from unittest import TestCase
from datetime import datetime
from classes.voting import Video
from functions.video_rules import check_blacklist, check_upload_date, check_duration


class TestFunctionsVideoRules(TestCase):
    def test_check_blacklist(self):
        videos = [
            Video({"title": "Example Video 1", "uploader": "Sunny Starscout"}),
            Video({"title": "Example Video 2", "uploader": "LittleshyFiM"}),
            Video({"title": "Example Video 3", "uploader": "Izzy Moonbow"}),
            Video({"title": "Example Video 4", "uploader": "Pipp Petals"}),
            Video({"title": "Example Video 5", "uploader": "Pipp Petals"}),
            Video({"title": "Example Video 6", "uploader": "Hitch Trailblazer"}),
        ]

        blacklisted_uploaders = ["LittleshyFiM", "Pipp Petals", "hawthornbunny"]

        check_blacklist(videos, blacklisted_uploaders)

        self.assertFalse(videos[0].annotations.has("BLACKLISTED"))
        self.assertTrue(videos[1].annotations.has("BLACKLISTED"))
        self.assertFalse(videos[2].annotations.has("BLACKLISTED"))
        self.assertTrue(videos[3].annotations.has("BLACKLISTED"))
        self.assertTrue(videos[4].annotations.has("BLACKLISTED"))
        self.assertFalse(videos[5].annotations.has("BLACKLISTED"))

    def test_check_upload_date(self):
        videos = [
            # Too old
            Video({"title": "Example Video 1", "upload_date": datetime(1912, 4, 15)}),
            Video({"title": "Example Video 2", "upload_date": datetime(2000, 1, 1)}),
            Video({"title": "Example Video 3", "upload_date": datetime(2000, 1, 1)}),
            Video({"title": "Example Video 4", "upload_date": datetime(2023, 2, 14)}),
            Video({"title": "Example Video 5", "upload_date": datetime(2023, 12, 31)}),
            Video({"title": "Example Video 6", "upload_date": datetime(2024, 1, 1)}),
            Video({"title": "Example Video 7", "upload_date": datetime(2024, 1, 31)}),
            # Within date
            Video({"title": "Example Video 8", "upload_date": datetime(2024, 2, 1)}),
            Video({"title": "Example Video 9", "upload_date": datetime(2024, 2, 1)}),
            Video({"title": "Example Video 10", "upload_date": datetime(2024, 2, 14)}),
            Video({"title": "Example Video 11", "upload_date": datetime(2024, 2, 28)}),
            Video({"title": "Example Video 12", "upload_date": datetime(2024, 2, 29)}),
            # Too new
            Video({"title": "Example Video 13", "upload_date": datetime(2024, 3, 1)}),
            Video({"title": "Example Video 14", "upload_date": datetime(2024, 3, 2)}),
            Video({"title": "Example Video 15", "upload_date": datetime(2024, 4, 1)}),
            Video({"title": "Example Video 16", "upload_date": datetime(2024, 12, 31)}),
            Video({"title": "Example Video 17", "upload_date": datetime(2025, 2, 1)}),
            Video({"title": "Example Video 18", "upload_date": datetime(2025, 2, 14)}),
            Video({"title": "Example Video 19", "upload_date": datetime(2025, 2, 28)}),
            Video({"title": "Example Video 20", "upload_date": datetime(2025, 3, 1)}),
            Video({"title": "Example Video 21", "upload_date": datetime(3025, 1, 1)}),
            Video({"title": "Example Video 22", "upload_date": datetime(9999, 12, 31)}),
        ]

        month_date = datetime(2024, 2, 14)
        check_upload_date(videos, month_date)

        self.assertTrue(videos[0].annotations.has("VIDEO TOO OLD"))
        self.assertTrue(videos[1].annotations.has("VIDEO TOO OLD"))
        self.assertTrue(videos[2].annotations.has("VIDEO TOO OLD"))
        self.assertTrue(videos[3].annotations.has("VIDEO TOO OLD"))
        self.assertTrue(videos[4].annotations.has("VIDEO TOO OLD"))
        self.assertTrue(videos[5].annotations.has("VIDEO TOO OLD"))
        self.assertTrue(videos[6].annotations.has("VIDEO TOO OLD"))
        self.assertTrue(videos[7].annotations.has_none())
        self.assertTrue(videos[8].annotations.has_none())
        self.assertTrue(videos[9].annotations.has_none())
        self.assertTrue(videos[10].annotations.has_none())
        self.assertTrue(videos[11].annotations.has_none())
        self.assertTrue(videos[12].annotations.has("VIDEO TOO NEW"))
        self.assertTrue(videos[13].annotations.has("VIDEO TOO NEW"))
        self.assertTrue(videos[14].annotations.has("VIDEO TOO NEW"))
        self.assertTrue(videos[15].annotations.has("VIDEO TOO NEW"))
        self.assertTrue(videos[16].annotations.has("VIDEO TOO NEW"))
        self.assertTrue(videos[17].annotations.has("VIDEO TOO NEW"))
        self.assertTrue(videos[18].annotations.has("VIDEO TOO NEW"))
        self.assertTrue(videos[19].annotations.has("VIDEO TOO NEW"))
        self.assertTrue(videos[20].annotations.has("VIDEO TOO NEW"))
        self.assertTrue(videos[21].annotations.has("VIDEO TOO NEW"))

    def test_check_duration(self):
        videos = [
            Video({"title": "Example Video 1", "duration": 0}),
            Video({"title": "Example Video 2", "duration": 1}),
            Video({"title": "Example Video 3", "duration": 29}),
            Video({"title": "Example Video 4", "duration": 30}),
            Video({"title": "Example Video 5", "duration": 31}),
            Video({"title": "Example Video 6", "duration": 44}),
            Video({"title": "Example Video 7", "duration": 45}),
            Video({"title": "Example Video 8", "duration": 46}),
            Video({"title": "Example Video 9", "duration": 60}),
            Video({"title": "Example Video 10", "duration": 1000000}),
        ]

        check_duration(videos)

        self.assertTrue(videos[0].annotations.has("VIDEO TOO SHORT"))
        self.assertTrue(videos[1].annotations.has("VIDEO TOO SHORT"))
        self.assertTrue(videos[2].annotations.has("VIDEO TOO SHORT"))
        self.assertTrue(videos[3].annotations.has("VIDEO TOO SHORT"))
        self.assertTrue(videos[4].annotations.has("VIDEO MAYBE TOO SHORT"))
        self.assertTrue(videos[5].annotations.has("VIDEO MAYBE TOO SHORT"))
        self.assertTrue(videos[6].annotations.has("VIDEO MAYBE TOO SHORT"))
        self.assertTrue(videos[7].annotations.has_none())
        self.assertTrue(videos[8].annotations.has_none())
        self.assertTrue(videos[9].annotations.has_none())
