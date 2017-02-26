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


def test_assignment_start_for_avtalegiro_payment_requests():
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


def test_assignment_start_for_avtalegiro_cancellation():
    record = netsgiro.AssignmentStart.from_string(
        'NY21362000000000040000868888888888800000'
        '0000000000000000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.record_type == netsgiro.RecordType.ASSIGNMENT_START

    assert record.assignment_type == (
        netsgiro.AvtaleGiroAssignmentType.CANCELLATIONS)

    assert record.agreement_id is None
    assert record.assignment_number == '4000086'
    assert record.assignment_account == '88888888888'


def test_assignment_start_for_ocr_giro_transactions():
    record = netsgiro.AssignmentStart.from_string(
        'NY09002000100856600000029999104276400000'
        '0000000000000000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.OCR_GIRO
    assert record.record_type == netsgiro.RecordType.ASSIGNMENT_START

    assert record.assignment_type == (
        netsgiro.AvtaleGiroAssignmentType.PAYMENT_REQUESTS)  # TODO Rename

    assert record.agreement_id == '001008566'
    assert record.assignment_number == '0000002'
    assert record.assignment_account == '99991042764'


def test_assignment_end_for_avtalegiro_payment_requests():
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


def test_assignment_end_for_avtalegiro_cancellations():
    record = netsgiro.AssignmentEnd.from_string(
        'NY21368800000006000000200000000000000060'
        '0170604170604000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.record_type == netsgiro.RecordType.ASSIGNMENT_END

    assert record.assignment_type == (
        netsgiro.AvtaleGiroAssignmentType.CANCELLATIONS)

    assert record.num_transactions == 6
    assert record.num_records == 20
    assert record.total_amount == 600
    assert record.nets_date == date(2004, 6, 17)
    assert record.nets_date_earliest == date(2004, 6, 17)
    assert record.nets_date_latest is None


def test_assignment_end_for_ocr_giro_transactions():
    record = netsgiro.AssignmentEnd.from_string(
        'NY09008800000020000000420000000000514490'
        '0200192200192200192000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.OCR_GIRO
    assert record.record_type == netsgiro.RecordType.ASSIGNMENT_END

    assert record.assignment_type == (
        netsgiro.AvtaleGiroAssignmentType.PAYMENT_REQUESTS)  # TODO: Rename

    assert record.num_transactions == 20
    assert record.num_records == 42
    assert record.total_amount == 5144900
    assert record.nets_date == date(1992, 1, 20)
    assert record.nets_date_earliest == date(1992, 1, 20)
    assert record.nets_date_latest == date(1992, 1, 20)


def test_transaction_amount_item_1_for_avtalegiro_payment_request():
    record = netsgiro.TransactionAmountItem1.from_string(
        'NY2121300000001170604           00000000'
        '000000100          008000011688373000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.record_type == netsgiro.RecordType.TRANSACTION_AMOUNT_1

    assert record.transaction_type == (
        netsgiro.TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK)
    assert record.transaction_number == '0000001'

    assert record.nets_date == date(2004, 6, 17)
    assert record.amount == 100
    assert record.kid == '008000011688373'


def test_transaction_amount_item_1_for_avtalegiro_cancellation():
    record = netsgiro.TransactionAmountItem1.from_string(
        'NY2193300000001170604           00000000'
        '000000100          008000011688373000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.record_type == netsgiro.RecordType.TRANSACTION_AMOUNT_1

    assert record.transaction_type == (
        netsgiro.TransactionType.AVTALEGIRO_CANCELLATION)
    assert record.transaction_number == '0000001'

    assert record.nets_date == date(2004, 6, 17)
    assert record.amount == 100
    assert record.kid == '008000011688373'


def test_transaction_amount_item_1_for_ocr_giro_transactions():
    record = netsgiro.TransactionAmountItem1.from_string(
        'NY09103000000012001921320101464000000000'
        '000102000                  0000531000000'
    )

    assert record.service_code == netsgiro.ServiceCode.OCR_GIRO
    assert record.record_type == netsgiro.RecordType.TRANSACTION_AMOUNT_1

    assert record.transaction_type == (
        netsgiro.TransactionType.FROM_GIRO_DEBITED_ACCOUNT)
    assert record.transaction_number == '0000001'

    assert record.nets_date == date(1992, 1, 20)

    assert record.centre_id == '13'
    assert record.day_code == 20
    assert record.partial_settlement_number == 1
    assert record.partial_settlement_serial_number == '01464'
    assert record.sign == '0'  # TODO Change type?

    assert record.amount == 102000
    assert record.kid == '0000531'


def test_transaction_amount_item_2_for_avtalegiro_payment_request():
    record = netsgiro.TransactionAmountItem2.from_string(
        'NY2121310000001NAVN                     '
        '                                   00000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.record_type == netsgiro.RecordType.TRANSACTION_AMOUNT_2

    assert record.transaction_type == (
        netsgiro.TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK)
    assert record.transaction_number == '0000001'

    assert record.payer_name == 'NAVN'
    assert record.reference is None


def test_transaction_amount_item_2_for_ocr_giro_transactions():
    record = netsgiro.TransactionAmountItem2.from_string(
        'NY09103100000019636827194099038562000000'
        '0160192999905123410000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.OCR_GIRO
    assert record.record_type == netsgiro.RecordType.TRANSACTION_AMOUNT_2

    assert record.transaction_type == (
        netsgiro.TransactionType.FROM_GIRO_DEBITED_ACCOUNT)
    assert record.transaction_number == '0000001'

    assert record.form_number == '9636827194'
    assert record.payer_name is None
    assert record.reference == '099038562'
    assert record.bank_date == date(1992, 1, 16)
    assert record.debit_account == '99990512341'


def test_transaction_amount_item_3_for_ocr_giro_transactions():
    record = netsgiro.TransactionAmountItem3.from_string(
        'NY0921320000001Foo bar baz              '
        '               0000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.OCR_GIRO
    assert record.record_type == netsgiro.RecordType.TRANSACTION_AMOUNT_3

    assert record.transaction_type == (
        netsgiro.TransactionType.PURCHASE_WITH_TEXT)
    assert record.transaction_number == '0000001'

    assert record.text == 'Foo bar baz'


def test_transaction_specification_for_avtalegiro_payment_request():
    record = netsgiro.TransactionSpecification.from_string(
        'NY212149000000140011 Gjelder Faktura: 16'
        '8837  Dato: 19/03/0400000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.record_type == netsgiro.RecordType.TRANSACTION_SPECIFICATION

    assert record.transaction_type == (
        netsgiro.TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK)
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
        netsgiro.TransactionType.AVTALEGIRO_AGREEMENTS)
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
        netsgiro.TransactionType.AVTALEGIRO_AGREEMENTS)
    assert record.transaction_number == '0000001'

    assert record.registration_type == (
        netsgiro.AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENTS)
    assert record.kid == '008000011688373'
    assert record.notify is False
