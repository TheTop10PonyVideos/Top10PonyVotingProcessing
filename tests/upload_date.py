from datetime import datetime
from unittest import TestCase
from pytz import timezone
from modules.upload_date import get_preceding_month, get_month_bounds, compare_date_to_bounds


class TestUploadDate(TestCase):
    def test_get_preceding_month(self):
        tz = timezone("Etc/GMT-14")
        today = datetime.now()
        self.assertEqual(today.month - 1, get_preceding_month(tz))
        
    def test_get_month_bounds(self):
        tz = timezone("Etc/GMT-14")

        # Test January to November
        for month in range(1, 12):
            lower_bound, upper_bound = get_month_bounds(month, tz)
            self.assertEqual(lower_bound.year, upper_bound.year)
            self.assertEqual(1, upper_bound.day)
            self.assertEqual(month, lower_bound.month)
            self.assertEqual(month+1, upper_bound.month)
            self.assertEqual(1, lower_bound.day)
            self.assertEqual(1, upper_bound.day)

        # Test that December's upper bound is the start of next year
        lower_bound, upper_bound = get_month_bounds(12, tz)
        self.assertEqual(12, lower_bound.month)
        self.assertEqual(1, upper_bound.month)
        self.assertEqual(lower_bound.year+1, upper_bound.year)
        
    def test_compare_date_to_bounds(self):
        # Check bounds: 1st Feburary 2024 to 1st March 2024
        lower_bound = datetime(2024, 2, 1)
        upper_bound = datetime(2024, 3, 1)

        # These dates are all in February, and so should all fall within the
        # bounds. (Note that 2024 was a leap year, so February did have 29 days
        # that year).
        dates = [
            datetime(2024, 2, 1),
            datetime(2024, 2, 2),
            datetime(2024, 2, 14),
            datetime(2024, 2, 28),
            datetime(2024, 2, 29),
        ]
        for date in dates:
            self.assertEqual(0, compare_date_to_bounds(date, lower_bound, upper_bound))

        # These dates should all be considered "too old".
        dates = [
            datetime(1912, 4, 15),
            datetime(2000, 1, 1),
            datetime(2000, 1, 1),
            datetime(2023, 2, 14),
            datetime(2023, 12, 31),
            datetime(2024, 1, 1),
            datetime(2024, 1, 31),
        ]
        for date in dates:
            self.assertEqual(-1, compare_date_to_bounds(date, lower_bound, upper_bound))

        # These dates should all be considered "too old".
        dates = [
            # This date is 1st March 2024, which matches the upper bound; however,
            # the comparison requires that the date be less than the upper bound, so
            # this should still be considered "too new".
            datetime(2024, 3, 1),
            datetime(2024, 3, 2),
            datetime(2024, 4, 1),
            datetime(2024, 12, 31),
            datetime(2025, 2, 1),
            datetime(2025, 2, 14),
            datetime(2025, 2, 28),
            datetime(2025, 3, 1),
            datetime(3025, 1, 1),
            datetime(9999, 12, 31),
        ]
        for date in dates:
            self.assertEqual(1, compare_date_to_bounds(date, lower_bound, upper_bound))

        # Check bounds: 1st December 2024 to 1st January 2025
        lower_bound = datetime(2024, 12, 1)
        upper_bound = datetime(2025, 1, 1)

        date = datetime(2024, 11, 30)
        self.assertEqual(-1, compare_date_to_bounds(date, lower_bound, upper_bound))

        date = datetime(2024, 11, 30, 23, 59, 59)
        self.assertEqual(-1, compare_date_to_bounds(date, lower_bound, upper_bound))

        date = datetime(2024, 12, 1)
        self.assertEqual(0, compare_date_to_bounds(date, lower_bound, upper_bound))

        date = datetime(2024, 12, 25)
        self.assertEqual(0, compare_date_to_bounds(date, lower_bound, upper_bound))

        date = datetime(2024, 12, 31)
        self.assertEqual(0, compare_date_to_bounds(date, lower_bound, upper_bound))

        date = datetime(2024, 12, 31, 23, 59, 59)
        self.assertEqual(0, compare_date_to_bounds(date, lower_bound, upper_bound))

        date = datetime(2025, 1, 1)
        self.assertEqual(1, compare_date_to_bounds(date, lower_bound, upper_bound))

        # Check bounds: 1st January 2025 to 1st February 2025
        lower_bound = datetime(2025, 1, 1)
        upper_bound = datetime(2025, 2, 1)

        date = datetime(2024, 12, 31)
        self.assertEqual(-1, compare_date_to_bounds(date, lower_bound, upper_bound))

        date = datetime(2024, 12, 31, 23, 59, 59)
        self.assertEqual(-1, compare_date_to_bounds(date, lower_bound, upper_bound))

        date = datetime(2025, 1, 1)
        self.assertEqual(0, compare_date_to_bounds(date, lower_bound, upper_bound))

        date = datetime(2025, 1, 15)
        self.assertEqual(0, compare_date_to_bounds(date, lower_bound, upper_bound))

        date = datetime(2025, 1, 31)
        self.assertEqual(0, compare_date_to_bounds(date, lower_bound, upper_bound))

        date = datetime(2025, 1, 31, 23, 59, 59)
        self.assertEqual(0, compare_date_to_bounds(date, lower_bound, upper_bound))

        date = datetime(2025, 2, 1)
        self.assertEqual(1, compare_date_to_bounds(date, lower_bound, upper_bound))

