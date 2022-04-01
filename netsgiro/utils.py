from contextlib import suppress
from datetime import date, datetime, timedelta
from typing import NoReturn
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

if TYPE_CHECKING:
    from attr import Attribute
    from netsgiro import PaymentRequest

__all__ = ['get_minimum_due_date']

# Nets operates in the Norwegian timezone, so that's what we'll use
OSLO_TZ = ZoneInfo('Europe/Oslo')


def get_minimum_due_date() -> date:
    """Return the minimum viable due date for a an ocrgiro created right now."""
    now = datetime.now(tz=OSLO_TZ)

    # 14:00 is the cut-off for sending in new transmissions;
    # files sent after 14:00 are processed the following day.
    delta = (
        4 if now.time() < datetime.strptime('02:00PM', '%I:%M%p').time() else 5
    )

    # Adjust for holidays, if the client has the optional dependency installed
    with suppress(ImportError):
        from holidays import country_holidays

        norwegian_holidays = country_holidays('NO')
        number_of_holidays = len(
            norwegian_holidays[
            now.strftime('%x'): (now + timedelta(days=delta)).strftime(
                '%x'
            )
            ]
        )
        delta += number_of_holidays

    return (now + timedelta(days=delta)).date()


def validate_minimum_date(inst: 'PaymentRequest', attr: 'Attribute', value: date) -> NoReturn:
    """Make sure payment request dates are gt the minimum allowed date."""
    if value < get_minimum_due_date():
        raise ValueError(
            'The minimum due date of a transaction is today + 4 calendar days.'
            ' OCR files with due dates earlier than this will be rejected when'
            ' submitted.'
        )
