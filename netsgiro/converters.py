def value_or_none(converter):
    """Converter that returns value or ``None``.

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
    """Converter that returns a truthy value or ``None``.

    ``converter`` is called to further convert non-``None`` values.
    """

    def truthy_or_none_converter(value):
        if not value:
            return None
        return converter(value)

    return truthy_or_none_converter


def stripped_spaces_around(converter):
    """Converter that returns a string stripped of leading and trailing spaces or
    ``None`` if the value isn't .

    ``converter`` is called to further convert non-``None`` values.
    """

    def stripped_text_converter(value):
        if value is None:
            return None
        return converter(value.strip())

    return stripped_text_converter


def stripped_newlines(converter):
    """Converter that returns a string stripped of newlines or ``None``.

    ``converter`` is called to further convert non-``None`` values.
    """

    def single_line_converter(value):
        if value is None:
            return None
        return converter(value.replace('\r', '').replace('\n', ''))

    return single_line_converter
