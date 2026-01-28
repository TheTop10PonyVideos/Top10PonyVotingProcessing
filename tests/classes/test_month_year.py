import pytest

from classes.month_year import MonthYear

def test_month_name():
    my = MonthYear(1, 2025) 
    assert my.month_name() == "Jan"

    my = MonthYear(2, 2026) 
    assert my.month_name() == "Feb"

    my = MonthYear(7, 2027) 
    assert my.month_name() == "Jul"

    my = MonthYear(12, 2028) 
    assert my.month_name() == "Dec"


def test_repr():
    my = MonthYear(1, 2025) 
    assert str(my) == "Jan 2025"

    my = MonthYear(2, 2026) 
    assert str(my) == "Feb 2026"

    my = MonthYear(7, 2027) 
    assert str(my) == "Jul 2027"

    my = MonthYear(12, 2028) 
    assert str(my) == "Dec 2028"


def test_add():
    my = MonthYear(1, 2025) 
    assert str(my) == "Jan 2025"
    my += 0
    assert str(my) == "Jan 2025"
    my += 1
    assert str(my) == "Feb 2025"
    my += 1
    assert str(my) == "Mar 2025"
    my += 9
    assert str(my) == "Dec 2025"
    my += 12
    assert str(my) == "Dec 2026"
    my += 2
    assert str(my) == "Feb 2027"


def test_sub():
    my = MonthYear(1, 2025) 
    assert str(my) == "Jan 2025"
    my -= 0
    assert str(my) == "Jan 2025"
    my -= 1
    assert str(my) == "Dec 2024"
    my -= 6
    assert str(my) == "Jun 2024"
    my -= 13
    assert str(my) == "May 2023"
    my -= 2
    assert str(my) == "Mar 2023"
