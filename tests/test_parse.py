import pytest

import netsgiro


def test_parse_empty_string_fails():
    with pytest.raises(ValueError) as exc_info:
        netsgiro.parse('')

    assert 'at least two lines' in str(exc_info)


def test_parse_too_short_lines_fails():
    with pytest.raises(ValueError) as exc_info:
        netsgiro.parse(
            'NY0000\n'
            'NY0000\n'
        )

    assert 'exactly 80 chars long' in str(exc_info)


def test_parse_payment_request(payment_request_data):
    transmission = netsgiro.parse(payment_request_data)

    assert isinstance(transmission, netsgiro.Transmission)
