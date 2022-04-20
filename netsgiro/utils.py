from contextlib import suppress
from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date, datetime

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo  # type: ignore[no-redef]

__all__ = ['get_minimum_due_date']

# Nets operates in the Norwegian timezone
OSLO_TZ = zoneinfo.ZoneInfo('Europe/Oslo')


def get_minimum_due_date(now: 'datetime') -> 'date':
    """
    Return the minimum valid due date for an avtalegiro ocrgiro created right now.

    The avtalegiro spec specifies that customers should have at least
    4 calendar days notice before a payment, so files containing due dates
    earlier than that will fail.

    "Calendar days" include weekends, but not holidays, so the holidays
    library is used to offset by holidays if it's installed.

    Logic is used for validation in netsgiro internally, but is also exported
    to be used downstream, when generating OCR files.
    """
    today = now.date()

    # 14:00 is the cut-off for sending in new transmissions;
    # files sent after 14:00 are processed the next day.
    delta = 4 if now.hour < 14 else 5

    # Adjust for holidays, if the dependency is installed
    # - Users of the library that want this, should install
    # - netsgiro with `pip install netsgiro[holidays]
    with suppress(ImportError):
        from holidays import country_holidays

        # Get holidays
        holidays_in_the_date_range = country_holidays('NO')[now : now + timedelta(days=delta)]  # type: ignore[misc]

        # Add days to `delta` for each holiday found in the date range
        delta += len(holidays_in_the_date_range)

    # Calendar days don't count weekends, but file do have
    # to be received on weekdays to be processed the same day
    if today.weekday() in [5, 6]:
        delta += 7 - today.weekday()

    return (now + timedelta(days=delta)).date()
