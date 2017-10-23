"""Custom converters for :mod:`attrs`."""


def value_or_none(converter):
    """Make converter that returns value or ``None``.

    ``converter`` is called to further convert non-``None`` values.

    This converter is identical to :func:`attr.converters.optional` in attrs >=
    17.1.0.
    """

    def value_or_none_converter(value):
        if value is None:
            return None
        return converter(value)

    return value_or_none_converter


def truthy_or_none(converter):
    """Make converter that returns a truthy value or ``None``.

    ``converter`` is called to further convert non-``None`` values.
    """

    def truthy_or_none_converter(value):
        if not value:
            return None
        return converter(value)

    return truthy_or_none_converter


def stripped_spaces_around(converter):
    """Make converter that strippes leading and trailing spaces.

    ``converter`` is called to further convert non-``None`` values.
    """

    def stripped_text_converter(value):
        if value is None:
            return None
        return converter(value.strip())

    return stripped_text_converter


def stripped_newlines(converter):
    """Make converter that returns a string stripped of newlines or ``None``.

    ``converter`` is called to further convert non-``None`` values.
    """

    def single_line_converter(value):
        if value is None:
            return None
        return converter(value.replace('\r', '').replace('\n', ''))

    return single_line_converter


def fixed_len_str(length, converter):
    """Make converter that pads a string to the given ``length`` or ``None``.

    ``converter`` is called to further converti non-``None`` values.
    """

    def fixed_len_str_converter(value):
        if value is None:
            return None
        return converter('{value:{length}}'.format(value=value, length=length))

    return fixed_len_str_converter
