from datetime import date

import pytest

import netsgiro
from netsgiro import objects


@pytest.fixture
def transmission():
    return netsgiro.Transmission(
        number='0000001',
        data_transmitter='12341234',
        data_recipient=netsgiro.NETS_ID,
        nets_date=date(2004, 6, 17),
    )


def test_transmission_from_zero_records_fails():
    with pytest.raises(ValueError) as exc_info:
        netsgiro.Transmission.from_records([])

    assert 'At least 2 records required, got 0' in str(exc_info)


def test_assignment_from_zero_records_fails():
    with pytest.raises(ValueError) as exc_info:
        netsgiro.Assignment.from_records([])

    assert 'At least 2 records required, got 0' in str(exc_info)


def make_specification_records(num_lines, num_columns=2):
    return [
        netsgiro.TransactionSpecification(
            service_code=netsgiro.ServiceCode.AVTALEGIRO,
            transaction_type=(
                netsgiro.TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION),
            transaction_number=1,
            line_number=line,
            column_number=column,
            text='Line {}, column {}'.format(line, column),
        )
        for line in range(1, num_lines + 1)
        for column in range(1, num_columns + 1)
    ]


def test_get_avtalegiro_specification_text_max_number_of_records():
    records = make_specification_records(42)

    result = objects.get_avtalegiro_specification_text(records)

    assert len(result.splitlines()) == 42
    assert 'Line 1, column 1' in result
    assert 'Line 42, column 2' in result


def test_get_avtalegiro_specification_text_too_many_records():
    records = make_specification_records(43)

    with pytest.raises(ValueError) as exc_info:
        objects.get_avtalegiro_specification_text(records)

    assert 'Max 84 specification records allowed, got 86' in str(exc_info)


def test_to_dict(transmission):
    assert transmission.to_dict() == {
        'number': '0000001',
        'data_transmitter': '12341234',
        'data_recipient': netsgiro.NETS_ID,
        'nets_date': date(2004, 6, 17),
        'assignments': [],
    }
