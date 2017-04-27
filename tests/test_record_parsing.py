from datetime import date

import pytest

import netsgiro
import netsgiro.records


def test_transmission_start():
    record = netsgiro.records.TransmissionStart.from_string(
        'NY00001055555555100008100008080000000000'
        '0000000000000000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.NONE
    assert record.RECORD_TYPE == netsgiro.RecordType.TRANSMISSION_START

    assert record.data_transmitter == '55555555'
    assert record.transmission_number == '1000081'
    assert record.data_recipient == '00008080'


def test_transmission_start_fails_when_invalid_format():
    line = 'XX' + ('0' * 78)

    with pytest.raises(ValueError) as exc_info:
        netsgiro.records.TransmissionStart.from_string(line)

    assert (
        '{!r} did not match TransmissionStart record format'.format(line)
        in str(exc_info)
    )


def test_transmission_end():
    record = netsgiro.records.TransmissionEnd.from_string(
        'NY00008900000006000000220000000000000060'
        '0170604000000000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.NONE
    assert record.RECORD_TYPE == netsgiro.RecordType.TRANSMISSION_END

    assert record.num_transactions == 6
    assert record.num_records == 22
    assert record.total_amount == 600
    assert record.nets_date == date(2004, 6, 17)


def test_assignment_start_for_avtalegiro_payment_requests():
    record = netsgiro.records.AssignmentStart.from_string(
        'NY21002000000000040000868888888888800000'
        '0000000000000000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == netsgiro.RecordType.ASSIGNMENT_START

    assert record.assignment_type == netsgiro.AssignmentType.TRANSACTIONS

    assert record.agreement_id == '000000000'
    assert record.assignment_number == '4000086'
    assert record.assignment_account == '88888888888'


def test_assignment_start_for_avtalegiro_agreements():
    record = netsgiro.records.AssignmentStart.from_string(
        'NY21242000000000040000868888888888800000'
        '0000000000000000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == netsgiro.RecordType.ASSIGNMENT_START

    assert record.assignment_type == (
        netsgiro.AssignmentType.AVTALEGIRO_AGREEMENTS)

    assert record.agreement_id is None
    assert record.assignment_number == '4000086'
    assert record.assignment_account == '88888888888'


def test_assignment_start_for_avtalegiro_cancellation():
    record = netsgiro.records.AssignmentStart.from_string(
        'NY21362000000000040000868888888888800000'
        '0000000000000000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == netsgiro.RecordType.ASSIGNMENT_START

    assert record.assignment_type == (
        netsgiro.AssignmentType.AVTALEGIRO_CANCELLATIONS)

    assert record.agreement_id is None
    assert record.assignment_number == '4000086'
    assert record.assignment_account == '88888888888'


def test_assignment_start_for_ocr_giro_transactions():
    record = netsgiro.records.AssignmentStart.from_string(
        'NY09002000100856600000029999104276400000'
        '0000000000000000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.OCR_GIRO
    assert record.RECORD_TYPE == netsgiro.RecordType.ASSIGNMENT_START

    assert record.assignment_type == netsgiro.AssignmentType.TRANSACTIONS

    assert record.agreement_id == '001008566'
    assert record.assignment_number == '0000002'
    assert record.assignment_account == '99991042764'


def test_assignment_end_for_avtalegiro_payment_requests():
    record = netsgiro.records.AssignmentEnd.from_string(
        'NY21008800000006000000200000000000000060'
        '0170604170604000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == netsgiro.RecordType.ASSIGNMENT_END

    assert record.assignment_type == netsgiro.AssignmentType.TRANSACTIONS

    assert record.num_transactions == 6
    assert record.num_records == 20
    assert record.total_amount == 600
    assert record.nets_date_earliest == date(2004, 6, 17)
    assert record.nets_date_latest == date(2004, 6, 17)


def test_assignment_end_for_avtalegiro_agreements():
    record = netsgiro.records.AssignmentEnd.from_string(
        'NY21248800000006000000200000000000000000'
        '0000000000000000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == netsgiro.RecordType.ASSIGNMENT_END

    assert record.assignment_type == (
        netsgiro.AssignmentType.AVTALEGIRO_AGREEMENTS)

    assert record.num_transactions == 6
    assert record.num_records == 20
    assert record.total_amount is None
    assert record.nets_date_earliest is None
    assert record.nets_date_latest is None


def test_assignment_end_for_avtalegiro_cancellations():
    record = netsgiro.records.AssignmentEnd.from_string(
        'NY21368800000006000000200000000000000060'
        '0170604170604000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == netsgiro.RecordType.ASSIGNMENT_END

    assert record.assignment_type == (
        netsgiro.AssignmentType.AVTALEGIRO_CANCELLATIONS)

    assert record.num_transactions == 6
    assert record.num_records == 20
    assert record.total_amount == 600
    assert record.nets_date_latest == date(2004, 6, 17)
    assert record.nets_date_earliest == date(2004, 6, 17)


def test_assignment_end_for_ocr_giro_transactions():
    record = netsgiro.records.AssignmentEnd.from_string(
        'NY09008800000020000000420000000000514490'
        '0200192200192200192000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.OCR_GIRO
    assert record.RECORD_TYPE == netsgiro.RecordType.ASSIGNMENT_END

    assert record.assignment_type == netsgiro.AssignmentType.TRANSACTIONS

    assert record.num_transactions == 20
    assert record.num_records == 42
    assert record.total_amount == 5144900
    assert record.nets_date == date(1992, 1, 20)
    assert record.nets_date_earliest == date(1992, 1, 20)
    assert record.nets_date_latest == date(1992, 1, 20)


def test_transaction_amount_item_1_for_avtalegiro_payment_request():
    record = netsgiro.records.TransactionAmountItem1.from_string(
        'NY2121300000001170604           00000000'
        '000000100          008000011688373000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == netsgiro.RecordType.TRANSACTION_AMOUNT_ITEM_1

    assert record.transaction_type == (
        netsgiro.TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION)
    assert record.transaction_number == 1

    assert record.nets_date == date(2004, 6, 17)
    assert record.amount == 100
    assert record.kid == '008000011688373'


def test_transaction_amount_item_1_for_avtalegiro_cancellation():
    record = netsgiro.records.TransactionAmountItem1.from_string(
        'NY2193300000001170604           00000000'
        '000000100          008000011688373000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == netsgiro.RecordType.TRANSACTION_AMOUNT_ITEM_1

    assert record.transaction_type == (
        netsgiro.TransactionType.AVTALEGIRO_CANCELLATION)
    assert record.transaction_number == 1

    assert record.nets_date == date(2004, 6, 17)
    assert record.amount == 100
    assert record.kid == '008000011688373'


def test_transaction_amount_item_1_for_ocr_giro_transactions():
    record = netsgiro.records.TransactionAmountItem1.from_string(
        'NY09103000000012001921320101464000000000'
        '000102000                  0000531000000'
    )

    assert record.service_code == netsgiro.ServiceCode.OCR_GIRO
    assert record.RECORD_TYPE == netsgiro.RecordType.TRANSACTION_AMOUNT_ITEM_1

    assert record.transaction_type == (
        netsgiro.TransactionType.FROM_GIRO_DEBITED_ACCOUNT)
    assert record.transaction_number == 1

    assert record.nets_date == date(1992, 1, 20)

    assert record.centre_id == '13'
    assert record.day_code == 20
    assert record.partial_settlement_number == 1
    assert record.partial_settlement_serial_number == '01464'
    assert record.sign == '0'

    assert record.amount == 102000
    assert record.kid == '0000531'


def test_transaction_amount_item_2_for_avtalegiro_payment_request():
    record = netsgiro.records.TransactionAmountItem2.from_string(
        'NY2121310000001NAVN                     '
        '                                   00000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == netsgiro.RecordType.TRANSACTION_AMOUNT_ITEM_2

    assert record.transaction_type == (
        netsgiro.TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION)
    assert record.transaction_number == 1

    assert record.payer_name == 'NAVN'
    assert record.reference is None


def test_transaction_amount_item_2_for_ocr_giro_transactions():
    record = netsgiro.records.TransactionAmountItem2.from_string(
        'NY09103100000019636827194099038562000000'
        '0160192999905123410000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.OCR_GIRO
    assert record.RECORD_TYPE == netsgiro.RecordType.TRANSACTION_AMOUNT_ITEM_2

    assert record.transaction_type == (
        netsgiro.TransactionType.FROM_GIRO_DEBITED_ACCOUNT)
    assert record.transaction_number == 1

    assert record.form_number == '9636827194'
    assert record.payer_name is None
    assert record.reference == '099038562'
    assert record.bank_date == date(1992, 1, 16)
    assert record.debit_account == '99990512341'


def test_transaction_amount_item_2_for_ocr_giro_with_data_in_filler_field():
    record = netsgiro.records.TransactionAmountItem2.from_string(
        'NY09103100000029797596016097596016188320'
        '6160192999910055240000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.OCR_GIRO
    assert record.RECORD_TYPE == netsgiro.RecordType.TRANSACTION_AMOUNT_ITEM_2

    assert record.transaction_type == (
        netsgiro.TransactionType.FROM_GIRO_DEBITED_ACCOUNT)
    assert record.transaction_number == 2

    assert record.form_number == '9797596016'
    assert record.payer_name is None
    assert record.reference == '097596016'
    assert record.bank_date == date(1992, 1, 16)
    assert record.debit_account == '99991005524'
    assert record._filler == '1883206'


def test_transaction_amount_item_3_for_ocr_giro_transactions():
    record = netsgiro.records.TransactionAmountItem3.from_string(
        'NY0921320000001Foo bar baz              '
        '               0000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.OCR_GIRO
    assert record.RECORD_TYPE == netsgiro.RecordType.TRANSACTION_AMOUNT_ITEM_3

    assert record.transaction_type == (
        netsgiro.TransactionType.PURCHASE_WITH_TEXT)
    assert record.transaction_number == 1

    assert record.text == 'Foo bar baz'


def test_transaction_specification_for_avtalegiro_payment_request():
    record = netsgiro.records.TransactionSpecification.from_string(
        'NY212149000000140011 Gjelder Faktura: 16'
        '8837  Dato: 19/03/0400000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == netsgiro.RecordType.TRANSACTION_SPECIFICATION

    assert record.transaction_type == (
        netsgiro.TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION)
    assert record.transaction_number == 1

    assert record.line_number == 1
    assert record.column_number == 1
    assert record.text == ' Gjelder Faktura: 168837  Dato: 19/03/04'


def make_specification_records(num_lines, num_columns=2):
    return [
        netsgiro.records.TransactionSpecification(
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


def test_transaction_specification_to_text_with_max_number_of_records():
    records = make_specification_records(42)

    result = netsgiro.records.TransactionSpecification.to_text(records)

    assert len(result.splitlines()) == 42
    assert 'Line 1, column 1' in result
    assert 'Line 42, column 2' in result


def test_transaction_specification_to_text_with_too_many_records():
    records = make_specification_records(43)

    with pytest.raises(ValueError) as exc_info:
        netsgiro.records.TransactionSpecification.to_text(records)

    assert 'Max 84 specification records allowed, got 86' in str(exc_info)


def test_avtalegiro_active_agreement():
    record = netsgiro.records.AvtaleGiroAgreement.from_string(
        'NY21947000000010          00800001168837'
        '3J00000000000000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == netsgiro.RecordType.TRANSACTION_AGREEMENTS

    assert record.transaction_type == (
        netsgiro.TransactionType.AVTALEGIRO_AGREEMENT)
    assert record.transaction_number == 1

    assert record.registration_type == (
        netsgiro.AvtaleGiroRegistrationType.ACTIVE_AGREEMENT)
    assert record.kid == '008000011688373'
    assert record.notify is True


def test_avtalegiro_new_or_updated_agreement():
    record = netsgiro.records.AvtaleGiroAgreement.from_string(
        'NY21947000000011          00800001168837'
        '3N00000000000000000000000000000000000000'
    )

    assert record.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == netsgiro.RecordType.TRANSACTION_AGREEMENTS

    assert record.transaction_type == (
        netsgiro.TransactionType.AVTALEGIRO_AGREEMENT)
    assert record.transaction_number == 1

    assert record.registration_type == (
        netsgiro.AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT)
    assert record.kid == '008000011688373'
    assert record.notify is False
