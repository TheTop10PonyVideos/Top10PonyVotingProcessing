from unittest import TestCase
from pytz import timezone
from datetime import datetime
from functions.date import parse_votes_csv_timestamp, format_votes_csv_timestamp, get_preceding_month_date, get_month_bounds, is_date_between

class TestFunctionsDate(TestCase):
    def test_parse_votes_csv_timestamp(self):
        timestamp = '4/1/2024 9:00:00'
        dt = parse_votes_csv_timestamp(timestamp)
        self.assertEqual('2024-04-01T09:00:00', dt.isoformat())

        timestamp = '12/31/2024 23:59:59'
        dt = parse_votes_csv_timestamp(timestamp)
        self.assertEqual('2024-12-31T23:59:59', dt.isoformat())

        timestamp = '02/02/2022 02:02:02'
        dt = parse_votes_csv_timestamp(timestamp)
        self.assertEqual('2022-02-02T02:02:02', dt.isoformat())

        timestamp = '11/6/2023 10:23:36'
        dt = parse_votes_csv_timestamp(timestamp)
        self.assertEqual('2023-11-06T10:23:36', dt.isoformat())

        timestamp = 'Invalid date string'
        with self.assertRaises(ValueError):
            dt = parse_votes_csv_timestamp(timestamp)

    def test_format_votes_csv_timestamp(self):
        dt = datetime(2024, 4, 1, 9, 0, 0)
        timestamp = format_votes_csv_timestamp(dt)
        self.assertEqual('4/1/2024 9:00:00', timestamp)

        dt = datetime(2024, 12, 25, 0, 0, 0)
        timestamp = format_votes_csv_timestamp(dt)
        self.assertEqual('12/25/2024 0:00:00', timestamp)

    def test_get_preceding_month_date(self):
        date = datetime(2024, 2, 14)
        self.assertEqual(datetime(2024, 1, 1), get_preceding_month_date(date))

    def test_get_month_bounds(self):
        # Test January to November
        for month in range(1, 12):
            date = datetime(2024, month, 14)
            lower_bound, upper_bound = get_month_bounds(date)
            self.assertEqual(lower_bound.year, upper_bound.year)
            self.assertEqual(1, upper_bound.day)
            self.assertEqual(month, lower_bound.month)
            self.assertEqual(month + 1, upper_bound.month)
            self.assertEqual(1, lower_bound.day)
            self.assertEqual(1, upper_bound.day)

        # Test that December's upper bound is the start of next year
        date = datetime(2024, 12, 25)
        lower_bound, upper_bound = get_month_bounds(date)
        self.assertEqual(12, lower_bound.month)
        self.assertEqual(1, upper_bound.month)
        self.assertEqual(lower_bound.year + 1, upper_bound.year)

    def test_is_date_between(self):
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
            self.assertTrue(is_date_between(date, lower_bound, upper_bound))

        # These dates should all be considered out of bounds.
        dates = [
            datetime(1912, 4, 15),
            datetime(2000, 1, 1),
            datetime(2000, 1, 1),
            datetime(2023, 2, 14),
            datetime(2023, 12, 31),
            datetime(2024, 1, 1),
            datetime(2024, 1, 31),
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
            self.assertFalse(is_date_between(date, lower_bound, upper_bound))

        # Check bounds: 1st December 2024 to 1st January 2025
        lower_bound = datetime(2024, 12, 1)
        upper_bound = datetime(2025, 1, 1)

        date = datetime(2024, 11, 30)
        self.assertFalse(is_date_between(date, lower_bound, upper_bound))

        date = datetime(2024, 11, 30, 23, 59, 59)
        self.assertFalse(is_date_between(date, lower_bound, upper_bound))

        date = datetime(2024, 12, 1)
        self.assertTrue(is_date_between(date, lower_bound, upper_bound))

        date = datetime(2024, 12, 25)
        self.assertTrue(is_date_between(date, lower_bound, upper_bound))

        date = datetime(2024, 12, 31)
        self.assertTrue(is_date_between(date, lower_bound, upper_bound))

        date = datetime(2024, 12, 31, 23, 59, 59)
        self.assertTrue(is_date_between(date, lower_bound, upper_bound))

        date = datetime(2025, 1, 1)
        self.assertFalse(is_date_between(date, lower_bound, upper_bound))

        # Check bounds: 1st January 2025 to 1st February 2025
        lower_bound = datetime(2025, 1, 1)
        upper_bound = datetime(2025, 2, 1)

        date = datetime(2024, 12, 31)
        self.assertFalse(is_date_between(date, lower_bound, upper_bound))

        date = datetime(2024, 12, 31, 23, 59, 59)
        self.assertFalse(is_date_between(date, lower_bound, upper_bound))

        date = datetime(2025, 1, 1)
        self.assertTrue(is_date_between(date, lower_bound, upper_bound))

        date = datetime(2025, 1, 15)
        self.assertTrue(is_date_between(date, lower_bound, upper_bound))

        date = datetime(2025, 1, 31)
        self.assertTrue(is_date_between(date, lower_bound, upper_bound))

        date = datetime(2025, 1, 31, 23, 59, 59)
        self.assertTrue(is_date_between(date, lower_bound, upper_bound))

        date = datetime(2025, 2, 1)
        self.assertFalse(is_date_between(date, lower_bound, upper_bound))
