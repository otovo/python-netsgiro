"""Custom validators for :mod:`attrs`."""
from typing import Any, Callable

from attr import Attribute
from attr.validators import instance_of

_C = Callable[[object, Attribute, Any], None]


def str_of_length(length: int) -> _C:
    """Validate that the value is a string of the given length."""

    def validator(
        instance: object, attribute: Attribute, value: Any
    ) -> None:
        instance_of(str)(instance, attribute, value)
        if len(value) != length:
            raise ValueError(
                '{0.name} must be exactly {1} chars, got {2!r}'.format(
                    attribute, length, value
                )
            )

    return validator


def str_of_max_length(length: int) -> _C:
    """Validate that the value is a string with a max length."""

    def validator(
        instance: object, attribute: Attribute, value: Any
    ) -> None:
        instance_of(str)(instance, attribute, value)
        if len(value) > length:
            raise ValueError(
                '{0.name} must be at most {1} chars, '
                'got {2!r} which is {3} chars'.format(
                    attribute, length, value, len(value)
                )
            )

    return validator
