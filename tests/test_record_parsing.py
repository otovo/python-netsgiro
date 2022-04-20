from datetime import date
from typing import List

import pytest

from netsgiro import (
    AssignmentType,
    AvtaleGiroRegistrationType,
    RecordType,
    ServiceCode,
    TransactionType,
)
from netsgiro.records import (
    AssignmentEnd,
    AssignmentStart,
    AvtaleGiroAgreement,
    Record,
    TransactionAmountItem1,
    TransactionAmountItem2,
    TransactionAmountItem3,
    TransactionSpecification,
    TransmissionEnd,
    TransmissionStart,
)


def test_transmission_start():
    record = TransmissionStart.from_string(
        'NY000010555555551000081000080800000000000000000000000000000000000000000000000000'
    )

    assert record.service_code == ServiceCode.NONE
    assert record.RECORD_TYPE == RecordType.TRANSMISSION_START

    assert record.data_transmitter == '55555555'
    assert record.transmission_number == '1000081'
    assert record.data_recipient == '00008080'


def test_transmission_start_fails_when_invalid_format():
    line = 'XX' + ('0' * 78)

    with pytest.raises(
        ValueError,
        match=f'{line!r} did not match TransmissionStart record format',
    ):
        TransmissionStart.from_string(line)


def test_transmission_end():
    record = TransmissionEnd.from_string(
        'NY000089000000060000002200000000000000600170604000000000000000000000000000000000'
    )

    assert record.service_code == ServiceCode.NONE
    assert record.RECORD_TYPE == RecordType.TRANSMISSION_END

    assert record.num_transactions == 6
    assert record.num_records == 22
    assert record.total_amount == 600
    assert record.nets_date == date(2004, 6, 17)


def test_assignment_start_for_avtalegiro_payment_requests():
    record = AssignmentStart.from_string(
        'NY210020000000000400008688888888888000000000000000000000000000000000000000000000'
    )

    assert record.service_code == ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == RecordType.ASSIGNMENT_START

    assert record.assignment_type == AssignmentType.TRANSACTIONS

    assert record.agreement_id == '000000000'
    assert record.assignment_number == '4000086'
    assert record.assignment_account == '88888888888'


def test_assignment_start_for_avtalegiro_agreements():
    record = AssignmentStart.from_string(
        'NY212420000000000400008688888888888000000000000000000000000000000000000000000000'
    )

    assert record.service_code == ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == RecordType.ASSIGNMENT_START

    assert record.assignment_type == AssignmentType.AVTALEGIRO_AGREEMENTS

    assert record.agreement_id is None
    assert record.assignment_number == '4000086'
    assert record.assignment_account == '88888888888'


def test_assignment_start_for_avtalegiro_cancellation():
    record = AssignmentStart.from_string(
        'NY213620000000000400008688888888888000000000000000000000000000000000000000000000'
    )

    assert record.service_code == ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == RecordType.ASSIGNMENT_START

    assert record.assignment_type == AssignmentType.AVTALEGIRO_CANCELLATIONS

    assert record.agreement_id is None
    assert record.assignment_number == '4000086'
    assert record.assignment_account == '88888888888'


def test_assignment_start_for_ocr_giro_transactions():
    record = AssignmentStart.from_string(
        'NY090020001008566000000299991042764000000000000000000000000000000000000000000000'
    )

    assert record.service_code == ServiceCode.OCR_GIRO
    assert record.RECORD_TYPE == RecordType.ASSIGNMENT_START

    assert record.assignment_type == AssignmentType.TRANSACTIONS

    assert record.agreement_id == '001008566'
    assert record.assignment_number == '0000002'
    assert record.assignment_account == '99991042764'


def test_assignment_end_for_avtalegiro_payment_requests():
    record = AssignmentEnd.from_string(
        'NY210088000000060000002000000000000000600170604170604000000000000000000000000000'
    )

    assert record.service_code == ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == RecordType.ASSIGNMENT_END

    assert record.assignment_type == AssignmentType.TRANSACTIONS

    assert record.num_transactions == 6
    assert record.num_records == 20
    assert record.total_amount == 600
    assert record.nets_date_earliest == date(2004, 6, 17)
    assert record.nets_date_latest == date(2004, 6, 17)


def test_assignment_end_for_avtalegiro_agreements():
    record = AssignmentEnd.from_string(
        'NY212488000000060000002000000000000000000000000000000000000000000000000000000000'
    )

    assert record.service_code == ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == RecordType.ASSIGNMENT_END

    assert record.assignment_type == AssignmentType.AVTALEGIRO_AGREEMENTS

    assert record.num_transactions == 6
    assert record.num_records == 20
    assert record.total_amount is None
    assert record.nets_date_earliest is None
    assert record.nets_date_latest is None


def test_assignment_end_for_avtalegiro_cancellations():
    record = AssignmentEnd.from_string(
        'NY213688000000060000002000000000000000600170604170604000000000000000000000000000'
    )

    assert record.service_code == ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == RecordType.ASSIGNMENT_END

    assert record.assignment_type == AssignmentType.AVTALEGIRO_CANCELLATIONS

    assert record.num_transactions == 6
    assert record.num_records == 20
    assert record.total_amount == 600
    assert record.nets_date_latest == date(2004, 6, 17)
    assert record.nets_date_earliest == date(2004, 6, 17)


def test_assignment_end_for_ocr_giro_transactions():
    record = AssignmentEnd.from_string(
        'NY090088000000200000004200000000005144900200192200192200192000000000000000000000'
    )

    assert record.service_code == ServiceCode.OCR_GIRO
    assert record.RECORD_TYPE == RecordType.ASSIGNMENT_END

    assert record.assignment_type == AssignmentType.TRANSACTIONS

    assert record.num_transactions == 20
    assert record.num_records == 42
    assert record.total_amount == 5144900
    assert record.nets_date == date(1992, 1, 20)
    assert record.nets_date_earliest == date(1992, 1, 20)
    assert record.nets_date_latest == date(1992, 1, 20)


def test_transaction_amount_item_1_for_avtalegiro_payment_request():
    record = TransactionAmountItem1.from_string(
        'NY2121300000001170604           00000000000000100          008000011688373000000'
    )

    assert record.service_code == ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == RecordType.TRANSACTION_AMOUNT_ITEM_1

    assert record.transaction_type == TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION
    assert record.transaction_number == 1

    assert record.nets_date == date(2004, 6, 17)
    assert record.amount == 100
    assert record.kid == '008000011688373'


def test_transaction_amount_item_1_for_avtalegiro_cancellation():
    record = TransactionAmountItem1.from_string(
        'NY2193300000001170604           00000000000000100          008000011688373000000'
    )

    assert record.service_code == ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == RecordType.TRANSACTION_AMOUNT_ITEM_1

    assert record.transaction_type == TransactionType.AVTALEGIRO_CANCELLATION
    assert record.transaction_number == 1

    assert record.nets_date == date(2004, 6, 17)
    assert record.amount == 100
    assert record.kid == '008000011688373'


def test_transaction_amount_item_1_for_ocr_giro_transactions():
    record = TransactionAmountItem1.from_string(
        'NY09103000000012001921320101464000000000000102000                  0000531000000'
    )

    assert record.service_code == ServiceCode.OCR_GIRO
    assert record.RECORD_TYPE == RecordType.TRANSACTION_AMOUNT_ITEM_1

    assert record.transaction_type == TransactionType.FROM_GIRO_DEBITED_ACCOUNT
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
    record = TransactionAmountItem2.from_string(
        'NY2121310000001NAVN                                                        00000'
    )

    assert record.service_code == ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == RecordType.TRANSACTION_AMOUNT_ITEM_2

    assert record.transaction_type == TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION
    assert record.transaction_number == 1

    assert record.payer_name == 'NAVN'
    assert record.reference is None


def test_transaction_amount_item_2_for_ocr_giro_transactions():
    record = TransactionAmountItem2.from_string(
        'NY091031000000196368271940990385620000000160192999905123410000000000000000000000'
    )

    assert record.service_code == ServiceCode.OCR_GIRO
    assert record.RECORD_TYPE == RecordType.TRANSACTION_AMOUNT_ITEM_2

    assert record.transaction_type == TransactionType.FROM_GIRO_DEBITED_ACCOUNT
    assert record.transaction_number == 1

    assert record.form_number == '9636827194'
    assert record.payer_name is None
    assert record.reference == '099038562'
    assert record.bank_date == date(1992, 1, 16)
    assert record.debit_account == '99990512341'


def test_transaction_amount_item_2_for_ocr_giro_with_data_in_filler_field():
    record = TransactionAmountItem2.from_string(
        'NY091031000000297975960160975960161883206160192999910055240000000000000000000000'
    )

    assert record.service_code == ServiceCode.OCR_GIRO
    assert record.RECORD_TYPE == RecordType.TRANSACTION_AMOUNT_ITEM_2

    assert record.transaction_type == TransactionType.FROM_GIRO_DEBITED_ACCOUNT
    assert record.transaction_number == 2

    assert record.form_number == '9797596016'
    assert record.payer_name is None
    assert record.reference == '097596016'
    assert record.bank_date == date(1992, 1, 16)
    assert record.debit_account == '99991005524'
    assert record._filler == '1883206'


def test_transaction_amount_item_3_for_ocr_giro_transactions():
    record = TransactionAmountItem3.from_string(
        'NY0921320000001Foo bar baz                             0000000000000000000000000'
    )

    assert record.service_code == ServiceCode.OCR_GIRO
    assert record.RECORD_TYPE == RecordType.TRANSACTION_AMOUNT_ITEM_3

    assert record.transaction_type == TransactionType.PURCHASE_WITH_TEXT
    assert record.transaction_number == 1

    assert record.text == 'Foo bar baz'


def test_transaction_specification_for_avtalegiro_payment_request():
    record = TransactionSpecification.from_string(
        'NY212149000000140011 Gjelder Faktura: 168837  Dato: 19/03/0400000000000000000000'
    )

    assert record.service_code == ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == RecordType.TRANSACTION_SPECIFICATION

    assert record.transaction_type == TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION
    assert record.transaction_number == 1

    assert record.line_number == 1
    assert record.column_number == 1
    assert record.text == ' Gjelder Faktura: 168837  Dato: 19/03/04'


def make_specification_records(
    num_lines: int, num_columns: int = 2
) -> List[TransactionSpecification]:
    return [
        TransactionSpecification(
            service_code=ServiceCode.AVTALEGIRO,
            transaction_type=TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION,
            transaction_number=1,
            line_number=line,
            column_number=column,
            text=f'Line {line}, column {column}',
        )
        for line in range(1, num_lines + 1)
        for column in range(1, num_columns + 1)
    ]


def test_transaction_specification_to_text_with_max_number_of_records():
    records = make_specification_records(42)

    result = TransactionSpecification.to_text(records)

    assert len(result.splitlines()) == 42
    assert 'Line 1, column 1' in result
    assert 'Line 42, column 2' in result


def test_transaction_specification_to_text_with_too_many_records():
    records = make_specification_records(43)

    with pytest.raises(ValueError, match='Max 84 specification records allowed, got 86'):
        TransactionSpecification.to_text(records)


def test_avtalegiro_active_agreement():
    record = AvtaleGiroAgreement.from_string(
        'NY21947000000010          008000011688373J00000000000000000000000000000000000000'
    )

    assert record.service_code == ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == RecordType.TRANSACTION_AGREEMENTS

    assert record.transaction_type == TransactionType.AVTALEGIRO_AGREEMENT
    assert record.transaction_number == 1

    assert record.registration_type == AvtaleGiroRegistrationType.ACTIVE_AGREEMENT
    assert record.kid == '008000011688373'
    assert record.notify is True


def test_avtalegiro_new_or_updated_agreement():
    record = AvtaleGiroAgreement.from_string(
        'NY21947000000011          008000011688373N00000000000000000000000000000000000000'
    )

    assert record.service_code == ServiceCode.AVTALEGIRO
    assert record.RECORD_TYPE == RecordType.TRANSACTION_AGREEMENTS

    assert record.transaction_type == TransactionType.AVTALEGIRO_AGREEMENT
    assert record.transaction_number == 1

    assert record.registration_type == AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT
    assert record.kid == '008000011688373'
    assert record.notify is False


def test__split_text_to_lines_and_columns_validation():
    """
    Make sure the validation in
    TransactionSpecification._split_text_to_lines_and_columns_validation works.
    """
    # Test <= max line count
    for i in [0, 1, 42]:
        for _ in TransactionSpecification._split_text_to_lines_and_columns('test\n' * i):
            pass

    # Test > max line count
    for i in [43, 100, 1000]:
        with pytest.raises(ValueError, match='Max 42 specification lines allowed'):
            for _ in TransactionSpecification._split_text_to_lines_and_columns('test\n' * i):
                pass

    # Test <= max line length
    for i in [0, 1, 80]:
        for _ in TransactionSpecification._split_text_to_lines_and_columns('i' * i):
            pass

    # Test > max line length
    for i in [81, 100, 1000]:
        with pytest.raises(ValueError, match='Specification lines must be max 80 chars long'):
            for _ in TransactionSpecification._split_text_to_lines_and_columns('i' * i):
                pass


def test_record__to_ocr():
    """Test that the record to_ocr abstract method is required."""

    class SomeRecordDerivative(Record):
        ...

    with pytest.raises(
        TypeError,
        match="Can't instantiate abstract class SomeRecordDerivative with abstract method to_ocr",
    ):
        SomeRecordDerivative()
