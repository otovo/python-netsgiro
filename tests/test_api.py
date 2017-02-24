from datetime import date

import pytest

import netsgiro
from netsgiro import records


def test_get_records_with_too_short_lines_fails():
    with pytest.raises(ValueError) as exc_info:
        netsgiro.get_records(
            'NY0000\n'
            'NY0000\n'
        )

    assert 'exactly 80 chars long' in str(exc_info)


def test_get_records(payment_request_data):
    result = netsgiro.get_records(payment_request_data)

    assert len(result) == 22

    transmission_start = result[0]
    assignment_start = result[1]
    transaction_amount_1 = result[2]
    transaction_amount_2 = result[3]
    transaction_spec_1 = result[4]
    transaction_spec_2 = result[5]
    assignment_end = result[20]
    transmission_end = result[21]

    assert isinstance(transmission_start, records.TransmissionStart)
    assert transmission_start.transmission_number == '1000081'
    assert transmission_start.data_recipient == netsgiro.NETS_ID

    assert isinstance(assignment_start, records.AssignmentStart)
    assert assignment_start.assignment_account == '88888888888'

    assert isinstance(transaction_amount_1, records.AvtaleGiroAmountItem1)
    assert transaction_amount_1.due_date == date(2004, 6, 17)
    assert transaction_amount_1.amount == 100
    assert transaction_amount_1.kid == '008000011688373'

    assert isinstance(transaction_amount_2, records.AvtaleGiroAmountItem2)
    assert transaction_amount_2.payer_name == 'NAVN'
    assert transaction_amount_2.reference is None

    assert isinstance(transaction_spec_1, records.AvtaleGiroSpecification)
    assert transaction_spec_1.text == (
        ' Gjelder Faktura: 168837  Dato: 19/03/04')

    assert isinstance(transaction_spec_2, records.AvtaleGiroSpecification)
    assert transaction_spec_2.text == (
        '                  ForfallsDato: 17/06/04')

    assert isinstance(assignment_end, records.AssignmentEnd)
    assert assignment_end.num_transactions == 6
    assert assignment_end.num_records == 20
    assert assignment_end.total_amount == 600
    assert assignment_end.nets_date == date(2004, 6, 17)
    assert assignment_end.nets_date_earliest == date(2004, 6, 17)
    assert assignment_end.nets_date_latest is None

    assert isinstance(transmission_end, records.TransmissionEnd)
    assert transmission_end.num_transactions == 6
    assert transmission_end.num_records == 22
    assert transmission_end.total_amount == 600
    assert transmission_end.nets_date == date(2004, 6, 17)
