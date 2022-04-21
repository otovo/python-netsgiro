from datetime import date
from decimal import Decimal

import pytest

import netsgiro


def test_transmission_with_single_payment_request_transaction():
    transmission = netsgiro.Transmission(
        number='1703231',
        data_transmitter='01234567',
        data_recipient=netsgiro.NETS_ID,
    )
    assignment = transmission.add_assignment(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        assignment_type=netsgiro.AssignmentType.TRANSACTIONS,
        number='0323001',
        account='15035382752',
    )
    assignment.add_payment_request(
        kid='000133700501645',
        due_date=date(2017, 4, 6),
        amount=Decimal('5244.63'),
        reference='ACME invoice #50164',
        payer_name='Wonderland',
        bank_notification=None,
    )
    assignment.add_payment_request(
        kid='001054300504897',
        due_date=date(2017, 4, 8),
        amount=Decimal('475.55'),
        reference='ACME invoice #50489',
        payer_name='Charlie',
        bank_notification='Foo bar',
    )

    records = list(transmission.to_records())

    assert len(records) == 10

    transmission_start = records[0]
    assignment_start = records[1]
    tx1_item1 = records[2]
    tx1_item2 = records[3]
    tx2_item1 = records[4]
    tx2_item2 = records[5]
    tx2_spec1 = records[6]
    tx2_spec2 = records[7]
    assignment_end = records[-2]
    transmission_end = records[-1]

    assert transmission_start.transmission_number == '1703231'
    assert transmission_start.data_transmitter == '01234567'
    assert transmission_start.data_recipient == netsgiro.NETS_ID
    assert transmission_end.nets_date == date(2017, 4, 6)

    assert assignment_start.assignment_number == '0323001'
    assert assignment_start.assignment_account == '15035382752'
    assert assignment_end.nets_date_earliest == date(2017, 4, 6)
    assert assignment_end.nets_date_latest == date(2017, 4, 8)

    assert tx1_item1.kid == '000133700501645'
    assert tx1_item1.amount == 524463
    assert tx1_item1.nets_date == date(2017, 4, 6)
    assert tx1_item2.reference == 'ACME invoice #50164'
    assert tx1_item2.payer_name == 'Wonderland'

    assert tx2_item1.kid == '001054300504897'
    assert tx2_item1.amount == 47555
    assert tx2_item1.nets_date == date(2017, 4, 8)
    assert tx2_item2.reference == 'ACME invoice #50489'
    assert tx2_item2.payer_name == 'Charlie'
    assert tx2_spec1.line_number == 1
    assert tx2_spec1.column_number == 1
    assert tx2_spec1.text == 'Foo bar                                 '
    assert tx2_spec2.line_number == 1
    assert tx2_spec2.column_number == 2
    assert tx2_spec2.text == '                                        '


assignment_data = {
    'kid': '000133700501645',
    'due_date': date(2017, 4, 6),
    'amount': Decimal('5244.63'),
    'reference': 'ACME invoice #50164',
    'payer_name': 'Wonderland',
    'bank_notification': False,
}


def test_transmission_add_payment_cancellation():
    """
    Test adding a payment cancellation.
    """
    transmission = netsgiro.Transmission(
        number='1703231',
        data_transmitter='01234567',
        data_recipient=netsgiro.NETS_ID,
    )
    assignment = transmission.add_assignment(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        assignment_type=netsgiro.AssignmentType.AVTALEGIRO_CANCELLATIONS,
        number='0323001',
        account='15035382752',
    )
    assignment.add_payment_cancellation(**assignment_data)

    records = list(transmission.to_records())

    assert len(records) == 6

    transmission_start = records[0]
    assignment_start = records[1]
    tx1_item1 = records[2]
    tx1_item2 = records[3]
    assignment_end = records[-2]
    transmission_end = records[-1]

    assert transmission_start.transmission_number == '1703231'
    assert transmission_start.data_transmitter == '01234567'
    assert transmission_start.data_recipient == netsgiro.NETS_ID
    assert transmission_end.nets_date == date(2017, 4, 6)

    assert assignment_start.assignment_number == '0323001'
    assert assignment_start.assignment_account == '15035382752'
    assert assignment_end.nets_date_earliest == date(2017, 4, 6)
    assert assignment_end.nets_date_latest == date(2017, 4, 6)

    assert tx1_item1.kid == '000133700501645'
    assert tx1_item1.amount == 524463
    assert tx1_item1.nets_date == date(2017, 4, 6)
    assert tx1_item2.reference == 'ACME invoice #50164'
    assert tx1_item2.payer_name == 'Wonderland'


def test_transmission_add_payment_cancellation_assertions():
    """
    Test add_payment_cancellation guards.
    """
    transmission = netsgiro.Transmission(
        number='1703231',
        data_transmitter='01234567',
        data_recipient=netsgiro.NETS_ID,
    )
    good_data = {
        'service_code': netsgiro.ServiceCode.AVTALEGIRO,
        'assignment_type': netsgiro.AssignmentType.AVTALEGIRO_CANCELLATIONS,
        'number': '0323001',
        'account': '15035382752',
    }

    # Test wrong service code
    bad_service_code_assignment = transmission.add_assignment(
        **(good_data | {'service_code': netsgiro.ServiceCode.OCR_GIRO})
    )
    with pytest.raises(AssertionError, match='Can only add cancellation to AvtaleGiro assignments'):
        bad_service_code_assignment.add_payment_cancellation(**assignment_data)

    # Test wrong assignment type
    bad_assignment_type_assignment = transmission.add_assignment(
        **(good_data | {'assignment_type': netsgiro.AssignmentType.AVTALEGIRO_AGREEMENTS})
    )
    with pytest.raises(
        AssertionError, match='Can only add cancellation to cancellation assignments'
    ):
        bad_assignment_type_assignment.add_payment_cancellation(**assignment_data)
