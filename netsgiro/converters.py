"""Custom converters for :mod:`attrs`."""
from typing import Any, Callable, Optional, TypeVar

T = TypeVar('T')
C = TypeVar('C', bound=Callable)  # type: ignore[type-arg]


def value_or_none(converter: C) -> Callable[[Any], Optional[T]]:
    """Make converter that returns value or ``None``.

    ``converter`` is called to further convert non-``None`` values.

    This converter is identical to :func:`attr.converters.optional` in attrs >=
    17.1.0.
    """
    return lambda value: None if value is None else converter(value)


def truthy_or_none(converter: C) -> Callable[[Any], Optional[T]]:
    """Make converter that returns a truthy value or ``None``.

    ``converter`` is called to further convert non-``None`` values.
    """
    return lambda value: converter(value) if value else None


def stripped_spaces_around(converter: C) -> Callable[[Any], Optional[T]]:
    """Make converter that strips leading and trailing spaces.

    ``converter`` is called to further convert non-``None`` values.
    """
    return lambda value: None if value is None else converter(value.strip())


def stripped_newlines(converter: C) -> Callable[[Any], Optional[T]]:
    """Make converter that returns a string stripped of newlines or ``None``.

    ``converter`` is called to further convert non-``None`` values.
    """
    return (
        lambda value: None
        if value is None
        else converter(value.replace('\r', '').replace('\n', ''))
    )


def fixed_len_str(length: int, converter: C) -> Callable[[Any], Optional[T]]:
    """Make converter that pads a string to the given ``length`` or ``None``.

    ``converter`` is called to further converti non-``None`` values.
    """
    return (
        lambda value: None
        if value is None
        else converter('{value:{length}}'.format(value=value, length=length))
    )
