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
