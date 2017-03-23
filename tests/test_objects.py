from datetime import date
from decimal import Decimal

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


def test_parse_payment_request(payment_request_data):
    transmission = netsgiro.parse(payment_request_data)

    assert isinstance(transmission, netsgiro.Transmission)
    assert transmission.number == '1000081'
    assert transmission.data_transmitter == '55555555'
    assert transmission.data_recipient == netsgiro.NETS_ID
    assert transmission.nets_date == date(2004, 6, 17)
    assert len(transmission.assignments) == 1

    assignment = transmission.assignments[0]

    assert isinstance(assignment, netsgiro.Assignment)
    assert assignment.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert assignment.type == netsgiro.AssignmentType.TRANSACTIONS
    assert assignment.agreement_id == '000000000'
    assert assignment.number == '4000086'
    assert assignment.account == '88888888888'
    assert len(assignment.transactions) == 6

    transaction = assignment.transactions[0]

    assert isinstance(transaction, netsgiro.Transaction)
    assert transaction.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert transaction.type == (
        netsgiro.TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION)
    assert transaction.number == 1
    assert transaction.nets_date == date(2004, 6, 17)
    assert transaction.amount == Decimal('1.00')
    assert transaction.amount_in_cents == 100
    assert transaction.kid == '008000011688373'
    assert transaction.reference is None
    assert transaction.text == (
        ' Gjelder Faktura: 168837  Dato: 19/03/04'
        '                  ForfallsDato: 17/06/04\n'
    )

    # Specific to AvtaleGiro
    assert transaction.payer_name == 'NAVN'


def test_parse_ocr_giro_transactions(ocr_giro_transactions_data):
    transmission = netsgiro.parse(ocr_giro_transactions_data)

    assert isinstance(transmission, netsgiro.Transmission)
    assert transmission.number == '0170031'
    assert transmission.data_transmitter == netsgiro.NETS_ID
    assert transmission.data_recipient == '00010200'
    assert transmission.nets_date == date(1992, 1, 20)
    assert len(transmission.assignments) == 1

    assignment = transmission.assignments[0]

    assert isinstance(assignment, netsgiro.Assignment)
    assert assignment.service_code == netsgiro.ServiceCode.OCR_GIRO
    assert assignment.type == netsgiro.AssignmentType.TRANSACTIONS
    assert assignment.agreement_id == '001008566'
    assert assignment.number == '0000002'
    assert assignment.account == '99991042764'
    assert len(assignment.transactions) == 20

    transaction = assignment.transactions[0]

    assert isinstance(transaction, netsgiro.Transaction)
    assert transaction.service_code == netsgiro.ServiceCode.OCR_GIRO
    assert transaction.type == (
        netsgiro.TransactionType.FROM_GIRO_DEBITED_ACCOUNT)
    assert transaction.number == 1
    assert transaction.nets_date == date(1992, 1, 20)
    assert transaction.amount == Decimal('1020')
    assert transaction.amount_in_cents == 102000
    assert transaction.kid == '0000531'
    assert transaction.reference == '099038562'
    assert transaction.text == 'Foo bar baz'

    # Specific to OCR Giro
    assert transaction.centre_id == '13'
    assert transaction.day_code == 20
    assert transaction.partial_settlement_number == 1
    assert transaction.partial_settlement_serial_number == '01464'
    assert transaction.sign == '0'
    assert transaction.form_number == '9636827194'
    assert transaction.bank_date == date(1992, 1, 16)
    assert transaction.debit_account == '99990512341'


def test_transmission_from_zero_records_fails():
    with pytest.raises(ValueError) as exc_info:
        objects.Transmission.from_records([])

    assert 'At least 2 records required, got 0' in str(exc_info)


def test_assignment_from_zero_records_fails():
    with pytest.raises(ValueError) as exc_info:
        objects.Assignment.from_records([])

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
