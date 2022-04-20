from datetime import datetime, timedelta

import holidays
import pytest

from netsgiro.utils import OSLO_TZ, get_minimum_due_date
from netsgiro.validators import validate_due_date

monday = datetime(2022, 3, 28, 13, 59, tzinfo=OSLO_TZ)


def test_minimum_due_date_before_cutoff():
    """
    Files generated before 14:00 Norwegian time should be
    adjusted by 4 days, minimum.
    """
    assert get_minimum_due_date(monday) == (monday + timedelta(days=4)).date()


monday_after_cutoff = datetime(2022, 4, 1, 14, 1, tzinfo=OSLO_TZ)


def test_minimum_due_date_after_cutoff():
    """
    Because files sent in after 14:00 are processed the next day, files
    generated after 14:00 Norwegian time should be adjusted by 5 days.
    """
    assert (
            get_minimum_due_date(monday_after_cutoff)
            == (monday_after_cutoff + timedelta(days=5)).date()
    )


day_before_easter = datetime(2022, 4, 13, 13, 59, tzinfo=OSLO_TZ)


def test_minimum_due_date_with_holidays_before_cutoff():
    """
    There are 2 holidays in the span 13-17th of April 2022,
    so we expect the function to adjust the timedelta by 2 days.
    """
    assert get_minimum_due_date(day_before_easter) == (day_before_easter + timedelta(days=6)).date()


day_before_easter_after_cutoff = datetime(2022, 4, 13, 23, 59, tzinfo=OSLO_TZ)


def test_minimum_due_date_with_holidays_after_cutoff():
    """
    If we send in the file after the cut-off, number of
    holidays is upped to 3, so we expect 2 more days of offsetting.
    """
    assert (
            get_minimum_due_date(day_before_easter_after_cutoff)
            == (day_before_easter_after_cutoff + timedelta(days=8)).date()
    )


friday = datetime(2022, 4, 1, 23, 59, tzinfo=OSLO_TZ)


def test_minimum_due_date_with_now_being_a_saturday():
    assert get_minimum_due_date(friday) == (friday + timedelta(days=5)).date()


def test_minimum_due_date_without_holiday_dependency():
    """
    Make sure an ImportError from a missing dependency isn't propagated.
    """
    import sys

    sys.modules['holidays'] = None
    assert get_minimum_due_date(monday) == (monday + timedelta(days=4)).date()
    sys.modules['holidays'] = holidays


def test_validate_due_date():
    with pytest.raises(ValueError, match='The minimum due date of a transaction'):
        validate_due_date(datetime.now().date())

    with pytest.raises(ValueError, match='The maximum due date of a transaction'):
        validate_due_date((datetime.now() + timedelta(days=366)).date())
