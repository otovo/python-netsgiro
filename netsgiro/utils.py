from contextlib import suppress
from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date, datetime

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

__all__ = ['get_minimum_due_date']

# Nets operates in the Norwegian timezone, so that's what we'll use
OSLO_TZ = zoneinfo.ZoneInfo('Europe/Oslo')


def get_minimum_due_date(now: 'datetime') -> 'date':
    """Return the minimum viable due date for a an ocrgiro created right now."""
    today = now.date()

    # 14:00 is the cut-off for sending in new transmissions;
    # files sent after 14:00 are processed the following day.
    delta = 5 if now.hour > 13 else 4

    # Adjust for holidays, if the client has the optional dependency installed
    with suppress(ImportError):
        from holidays import country_holidays

        delta += len(country_holidays('NO')[now : now + timedelta(days=delta)])

    # File have to be received on weekdays to be processed the same day
    if today.weekday() in [5, 6]:
        delta += 7 - today.weekday()

    return (now + timedelta(days=delta)).date()
