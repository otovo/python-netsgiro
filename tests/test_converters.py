import pytest

from netsgiro.converters import value_or_none, truthy_or_none, to_bool

values = [
    (int, None, None, None),
    (int, 1, 1, 1),
    (int, 1.5, 1, 1),
    (float, 1.5, 1.5, 1.5),
    (bool, 1.5, True, True),
    (bool, 0, False, None),  # different
]


@pytest.mark.parametrize('c, v, v1, v2', values)
def test_value_or_none(c, v, v1, v2):
    """
    Test the value or none and truthy or none converters.

    They're almost identical.
    """
    assert value_or_none(c)(v) == v1
    assert truthy_or_none(c)(v) == v2


def test_to_bool():
    assert to_bool(True) is True
    assert to_bool(False) is False
    assert to_bool('J') is True
    assert to_bool('N') is False
    for v in [None, 'S', '', [], {}]:
        with pytest.raises(ValueError, match="Expected 'J' or 'N', got "):
            to_bool(v)
