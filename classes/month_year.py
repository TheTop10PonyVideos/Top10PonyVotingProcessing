from math import floor

class MonthYear:
    """Represents a given month of a given year (e.g. April 2025), with a few
    useful manipulation methods."""

    month_names = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

    def __init__(self, month: int, year: int):
        if month < 1 or month > 12:
            raise ValueError(f"Cannot initialize month-year - invalid month {month}. month must be from 1 to 12")

        self.month = month
        self.year = year

    def month_name(self):
        return MonthYear.month_names[self.month - 1]

    def prev(self):
        return self - 1

    def next(self):
        return self + 1

    def __add__(self, num_months: int):
        month = (((self.month-1) + num_months) % 12) + 1
        year = self.year + floor((num_months+self.month-1) / 12)

        return MonthYear(month, year)

    def __sub__(self, num_months: int):
        return self + (0 - num_months)

    def __repr__(self):
        return f"{self.month_name()} {self.year}"
