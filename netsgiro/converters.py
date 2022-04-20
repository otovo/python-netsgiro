"""Custom converters for :mod:`attrs`."""
import datetime
from typing import Any, Callable, Optional, TypeVar, Union

from netsgiro.enums import (
    AssignmentType,
    AvtaleGiroRegistrationType,
    RecordType,
    ServiceCode,
    TransactionType,
)

T = TypeVar('T')


def to_int_or_none(value: Union[None, int, str]) -> Optional[int]:
    """Convert input to int or None."""
    return None if value is None else int(value)


def value_or_none(converter: Callable[[Any], T]) -> Callable[[Any], Optional[T]]:
    """Make converter that returns value or ``None``.

    ``converter`` is called to further convert non-``None`` values.

    This converter is identical to :func:`attr.converters.optional` in attrs >=
    17.1.0.
    """
    return lambda value: None if value is None else converter(value)


def truthy_or_none(converter: Callable[[Any], T]) -> Callable[[Any], Optional[T]]:
    """Make converter that returns a truthy value or ``None``.

    ``converter`` is called to further convert non-``None`` values.
    """
    return lambda value: converter(value) if value else None


def stripped_newlines(converter: Callable[[Any], T]) -> Callable[[Any], Optional[T]]:
    """Make converter that returns a string stripped of newlines or ``None``.

    ``converter`` is called to further convert non-``None`` values.
    """
    return lambda value: converter(value.replace('\r', '').replace('\n', ''))


def fixed_len_str(length: int, converter: Callable[[Any], T]) -> Callable[[Any], Optional[T]]:
    """Make converter that pads a string to the given ``length`` or ``None``.

    ``converter`` is called to further convert non-``None`` values.
    """
    return lambda value: converter('{value:{length}}'.format(value=value, length=length))


def to_safe_str_or_none(value: Optional[str]) -> Optional[str]:
    """Convert input to cleaned string or None."""
    if value is None:
        return None
    v = str(value.strip()).replace('\r', '').replace('\n', '')
    return v or None


def to_service_code(value: Union[ServiceCode, int, str]) -> ServiceCode:
    """Convert input to ServiceCode."""
    return ServiceCode(int(value))


def to_assignment_type(value: Union[AssignmentType, int, str]) -> AssignmentType:
    """Convert input to AssignmentType."""
    return AssignmentType(int(value))


def to_transaction_type(value: Union[TransactionType, int, str]) -> TransactionType:
    """Convert input to TransactionType."""
    return TransactionType(int(value))


def to_record_type(value: Union[RecordType, int, str]) -> RecordType:
    """Convert input to RecordType."""
    return RecordType(int(value))


def to_avtalegiro_registration_type(
    value: Union[AvtaleGiroRegistrationType, int, str]
) -> AvtaleGiroRegistrationType:
    """Convert input to AvtaleGiroRegistrationType."""
    return AvtaleGiroRegistrationType(int(value))


def to_date(value: Union[datetime.date, str]) -> datetime.date:
    """Convert input to date."""
    if isinstance(value, datetime.date):
        return value
    return datetime.datetime.strptime(value, '%d%m%y').date()


def to_date_or_none(value: Optional[Union[datetime.date, str]]) -> Optional[datetime.date]:
    """Convert input to date or None."""
    if isinstance(value, datetime.date):
        return value
    if value is None or value == '000000':
        return None
    return datetime.datetime.strptime(value, '%d%m%y').date()


def to_bool(value: Union[bool, str]) -> bool:
    """Convert input to bool."""
    if isinstance(value, bool):
        return value
    if value == 'J':
        return True
    elif value == 'N':
        return False
    else:
        raise ValueError(f"Expected 'J' or 'N', got {value!r}")
