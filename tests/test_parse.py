from pathlib import Path

import pytest

import netsgiro


TEST_DIR = Path(__file__).parent


@pytest.fixture
def payment_request_data():
    filepath = TEST_DIR / 'data' / 'avtalegiro_payment_request.txt'
    with filepath.open('r', encoding='iso-8859-1') as fh:
        return fh.read()


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
