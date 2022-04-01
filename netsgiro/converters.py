"""Custom converters for :mod:`attrs`."""
from typing import Any, Callable, Union

T = Callable[[Any], Union[int, str, bool, None]]
C = Union[type[int], type[str], type[bool]]


def value_or_none(converter: C) -> T:
    """Make converter that returns value or ``None``.

    ``converter`` is called to further convert non-``None`` values.

    This converter is identical to :func:`attr.converters.optional` in attrs >=
    17.1.0.
    """
    return lambda value: converter(value) if value is not None else None


def truthy_or_none(converter: C) -> T:
    """Make converter that returns a truthy value or ``None``.

    ``converter`` is called to further convert non-``None`` values.
    """
    return lambda value: converter(value) if value else None


def stripped_spaces_around(converter: C) -> T:
    """Make converter that strippes leading and trailing spaces.

    ``converter`` is called to further convert non-``None`` values.
    """
    return lambda value: converter(value.strip()) if value is not None else None


def stripped_newlines(converter: C) -> T:
    """Make converter that returns a string stripped of newlines or ``None``.

    ``converter`` is called to further convert non-``None`` values.
    """
    return (
        lambda value: converter(value.replace('\r', '').replace('\n', ''))
        if value is not None
        else None
    )


def fixed_len_str(length: int, converter: C) -> T:
    """Make converter that pads a string to the given ``length`` or ``None``.

    ``converter`` is called to further converti non-``None`` values.
    """
    return (
        lambda value: converter(f'{value:{length}}')
        if value is not None
        else None
    )
