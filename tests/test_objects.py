from datetime import date

import pytest

import netsgiro


@pytest.fixture
def transmission():
    return netsgiro.Transmission(
        number='0000001',
        data_transmitter='12341234',
        data_recipient=netsgiro.NETS_ID,
        date=date(2004, 6, 17),
    )


def test_transmission_from_zero_records_fails():
    with pytest.raises(ValueError) as exc_info:
        netsgiro.Transmission.from_records([])

    assert 'At least 2 records required, got 0' in str(exc_info)


def test_assignment_from_zero_records_fails():
    with pytest.raises(ValueError) as exc_info:
        netsgiro.Assignment.from_records([])

    assert 'At least 2 records required, got 0' in str(exc_info)
