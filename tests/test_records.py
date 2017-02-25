from datetime import date

import pytest

import netsgiro


def test_transmission_start():
    record = netsgiro.TransmissionStart.from_string(
        'NY00001055555555100008100008080000000000'
        '0000000000000000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.NONE
    assert record.record_type == netsgiro.RecordType.TRANSMISSION_START

    assert record.transmission_type == 0

    assert record.data_transmitter == '55555555'
    assert record.transmission_number == '1000081'
    assert record.data_recipient == '00008080'


def test_transmission_start_fails_when_invalid_format():
    line = 'XX' + ('0' * 78)

    with pytest.raises(ValueError) as exc_info:
        netsgiro.TransmissionStart.from_string(line)

    assert (
        '{!r} did not match TransmissionStart record format'.format(line)
        in str(exc_info)
    )


def test_transmission_end():
    record = netsgiro.TransmissionEnd.from_string(
        'NY00008900000006000000220000000000000060'
        '0170604000000000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.NONE
    assert record.record_type == netsgiro.RecordType.TRANSMISSION_END

    assert record.transmission_type == 0

    assert record.num_transactions == 6
    assert record.num_records == 22
    assert record.total_amount == 600
    assert record.nets_date == date(2004, 6, 17)


def test_assignment_start():
    record = netsgiro.AssignmentStart.from_string(
        'NY21002000000000040000868888888888800000'
        '0000000000000000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.record_type == netsgiro.RecordType.ASSIGNMENT_START

    assert record.assignment_type == (
        netsgiro.AvtaleGiroAssignmentType.PAYMENT_REQUESTS)

    assert record.agreement_id == '000000000'
    assert record.assignment_number == '4000086'
    assert record.assignment_account == '88888888888'


def test_assignment_start_for_avtalegiro_agreements():
    record = netsgiro.AssignmentStart.from_string(
        'NY21242000000000040000868888888888800000'
        '0000000000000000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.record_type == netsgiro.RecordType.ASSIGNMENT_START

    assert record.assignment_type == (
        netsgiro.AvtaleGiroAssignmentType.AGREEMENTS)

    assert record.agreement_id is None
    assert record.assignment_number == '4000086'
    assert record.assignment_account == '88888888888'


def test_assignment_end():
    record = netsgiro.AssignmentEnd.from_string(
        'NY21008800000006000000200000000000000060'
        '0170604170604000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.record_type == netsgiro.RecordType.ASSIGNMENT_END

    assert record.assignment_type == (
        netsgiro.AvtaleGiroAssignmentType.PAYMENT_REQUESTS)

    assert record.num_transactions == 6
    assert record.num_records == 20
    assert record.total_amount == 600
    assert record.nets_date == date(2004, 6, 17)
    assert record.nets_date_earliest == date(2004, 6, 17)
    assert record.nets_date_latest is None


def test_assignment_end_for_avtalegiro_agreements():
    record = netsgiro.AssignmentEnd.from_string(
        'NY21248800000006000000200000000000000000'
        '0000000000000000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.record_type == netsgiro.RecordType.ASSIGNMENT_END

    assert record.assignment_type == (
        netsgiro.AvtaleGiroAssignmentType.AGREEMENTS)

    assert record.num_transactions == 6
    assert record.num_records == 20
    assert record.total_amount is None
    assert record.nets_date is None
    assert record.nets_date_earliest is None
    assert record.nets_date_latest is None


def test_avtalegiro_amount_item_1():
    record = netsgiro.AvtaleGiroAmountItem1.from_string(
        'NY2121300000001170604           00000000'
        '000000100          008000011688373000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.record_type == netsgiro.RecordType.TRANSACTION_AMOUNT_1

    assert record.transaction_type == (
        netsgiro.AvtaleGiroTransactionType.NOTIFICATION_FROM_BANK)
    assert record.transaction_number == '0000001'

    assert record.due_date == date(2004, 6, 17)
    assert record.amount == 100
    assert record.kid == '008000011688373'


def test_avtalegiro_amount_item_2():
    record = netsgiro.AvtaleGiroAmountItem2.from_string(
        'NY2121310000001NAVN                     '
        '                                   00000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.record_type == netsgiro.RecordType.TRANSACTION_AMOUNT_2

    assert record.transaction_type == (
        netsgiro.AvtaleGiroTransactionType.NOTIFICATION_FROM_BANK)
    assert record.transaction_number == '0000001'

    assert record.payer_name == 'NAVN'
    assert record.reference is None


def test_avtalegiro_specification():
    record = netsgiro.AvtaleGiroSpecification.from_string(
        'NY212149000000140011 Gjelder Faktura: 16'
        '8837  Dato: 19/03/0400000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.record_type == netsgiro.RecordType.TRANSACTION_SPECIFICATION

    assert record.transaction_type == (
        netsgiro.AvtaleGiroTransactionType.NOTIFICATION_FROM_BANK)
    assert record.transaction_number == '0000001'

    assert record.line_number == 1
    assert record.column_number == 1
    assert record.text == ' Gjelder Faktura: 168837  Dato: 19/03/04'


def test_avtalegiro_all_agreements():
    record = netsgiro.AvtaleGiroAgreement.from_string(
        'NY21947000000010          00800001168837'
        '3J00000000000000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.record_type == netsgiro.RecordType.TRANSACTION_AGREEMENTS

    assert record.transaction_type == (
        netsgiro.AvtaleGiroTransactionType.AGREEMENTS)
    assert record.transaction_number == '0000001'

    assert record.registration_type == (
        netsgiro.AvtaleGiroRegistrationType.ALL_AGREEMENTS)
    assert record.kid == '008000011688373'
    assert record.notify is True


def test_avtalegiro_new_or_updated_agreements():
    record = netsgiro.AvtaleGiroAgreement.from_string(
        'NY21947000000011          00800001168837'
        '3N00000000000000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.record_type == netsgiro.RecordType.TRANSACTION_AGREEMENTS

    assert record.transaction_type == (
        netsgiro.AvtaleGiroTransactionType.AGREEMENTS)
    assert record.transaction_number == '0000001'

    assert record.registration_type == (
        netsgiro.AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENTS)
    assert record.kid == '008000011688373'
    assert record.notify is False
