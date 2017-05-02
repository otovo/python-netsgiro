from datetime import date

import pytest

import netsgiro
import netsgiro.records


def test_transmission_start():
    record = netsgiro.records.TransmissionStart(
        service_code=netsgiro.ServiceCode.NONE,
        transmission_number='1000081',
        data_transmitter='55555555',
        data_recipient=netsgiro.NETS_ID,
    )

    assert record.to_ocr() == (
        'NY00001055555555100008100008080000000000'
        '0000000000000000000000000000000000000000'
    )


@pytest.mark.parametrize(
    'transmission_number, data_transmitter, data_recipient, exc', [
        ('81', '55555555', '44444444', ValueError),
        (1000081, '55555555', '44444444', TypeError),
        ('1000081', '5555', '44444444', ValueError),
        ('1000081', 55555555, '44444444', TypeError),
        ('1000081', '55555555', '4444', ValueError),
        ('1000081', '55555555', 44444444, TypeError),
    ])
def test_transmission_start_with_invalid_data(
        transmission_number, data_transmitter, data_recipient, exc):
    with pytest.raises(exc):
        netsgiro.records.TransmissionStart(
            service_code=netsgiro.ServiceCode.NONE,
            transmission_number=transmission_number,
            data_transmitter=data_transmitter,
            data_recipient=data_recipient,
        )


def test_transmission_end():
    record = netsgiro.records.TransmissionEnd(
        service_code=netsgiro.ServiceCode.NONE,
        num_transactions=6,
        num_records=22,
        total_amount=600,
        nets_date=date(2004, 6, 17),
    )

    assert record.to_ocr() == (
        'NY00008900000006000000220000000000000060'
        '0170604000000000000000000000000000000000'
    )


@pytest.mark.parametrize(
    'num_tx, num_records, total_amount, nets_date, exc', [
        ('abc', 22, 600, date(2004, 6, 17), ValueError),
        (6, 'abc', 600, date(2004, 6, 17), ValueError),
        (6, 22, 'abc', date(2004, 6, 17), ValueError),
        (6, 22, 600, '2004-06-17', ValueError),
    ])
def test_transmission_end_with_invalid_data(
        num_tx, num_records, total_amount, nets_date, exc):
    with pytest.raises(exc):
        netsgiro.records.TransmissionEnd(
            service_code=netsgiro.ServiceCode.NONE,
            num_transactions=num_tx,
            num_records=num_records,
            total_amount=total_amount,
            nets_date=nets_date,
        )


def test_assignment_start_for_avtalegiro_payment_requests():
    record = netsgiro.records.AssignmentStart(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        assignment_type=netsgiro.AssignmentType.TRANSACTIONS,
        assignment_number='4000086',
        assignment_account='88888888888',
        agreement_id='000000111',
    )

    assert record.to_ocr() == (
        'NY21002000000011140000868888888888800000'
        '0000000000000000000000000000000000000000'
    )


def test_assignment_start_for_avtalegiro_agreements():
    record = netsgiro.records.AssignmentStart(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        assignment_type=netsgiro.AssignmentType.AVTALEGIRO_AGREEMENTS,
        assignment_number='4000086',
        assignment_account='88888888888',
        agreement_id=None,
    )

    assert record.to_ocr() == (
        'NY21242000000000040000868888888888800000'
        '0000000000000000000000000000000000000000'
    )


@pytest.mark.parametrize(
    'number, account, agreement_id, exc', [
        (4000086, '88888888888', '123456789', TypeError),
        ('86', '88888888888', '123456789', ValueError),
        ('4000086', 88888888888, '123456789', TypeError),
        ('4000086', '88', '123456789', ValueError),
        ('4000086', '88888888888', 123456789, TypeError),
        ('4000086', '88888888888', '6789', ValueError),
    ])
def test_assignment_start_with_invalid_data(
        number, account, agreement_id, exc):
    with pytest.raises(exc):
        netsgiro.records.AssignmentStart(
            service_code=netsgiro.ServiceCode.AVTALEGIRO,
            assignment_type=netsgiro.AssignmentType.TRANSACTIONS,
            assignment_number=number,
            assignment_account=account,
            agreement_id=agreement_id,
        )


def test_assignment_end_for_avtalegiro_payment_requests():
    record = netsgiro.records.AssignmentEnd(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        assignment_type=netsgiro.AssignmentType.TRANSACTIONS,
        num_transactions=6,
        num_records=20,
        total_amount=600,
        nets_date_1=date(2004, 6, 17),
        nets_date_2=date(2004, 6, 17),
    )

    assert record.to_ocr() == (
        'NY21008800000006000000200000000000000060'
        '0170604170604000000000000000000000000000'
    )


def test_assignment_end_for_avtalegiro_agreements():
    record = netsgiro.records.AssignmentEnd(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        assignment_type=netsgiro.AssignmentType.AVTALEGIRO_AGREEMENTS,
        num_transactions=6,
        num_records=20,
    )

    assert record.to_ocr() == (
        'NY21248800000006000000200000000000000000'
        '0000000000000000000000000000000000000000'
    )


def test_transaction_amount_item_1_for_ocr_giro_transactions():
    record = netsgiro.records.TransactionAmountItem1(
        service_code=netsgiro.ServiceCode.OCR_GIRO,
        transaction_type=netsgiro.TransactionType.FROM_GIRO_DEBITED_ACCOUNT,
        transaction_number=1,
        nets_date=date(1992, 1, 20),
        amount=102000,
        kid='0000531',

        centre_id='13',
        day_code=20,
        partial_settlement_number=1,
        partial_settlement_serial_number='01464',
        sign='0',
    )

    assert record.to_ocr() == (
        'NY09103000000012001921320101464000000000'
        '000102000                  0000531000000'
    )


def test_transaction_amount_item_1_for_avtalegiro_payment_requests():
    record = netsgiro.records.TransactionAmountItem1(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        transaction_type=(
            netsgiro.TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION),
        transaction_number=1,
        nets_date=date(2004, 6, 17),
        amount=100,
        kid='008000011688373',
    )

    assert record.to_ocr() == (
        'NY2121300000001170604           00000000'
        '000000100          008000011688373000000'
    )


def test_transaction_amount_item_2_for_avtalegiro_payment_request():
    record = netsgiro.records.TransactionAmountItem2(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        transaction_type=(
            netsgiro.TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION),
        transaction_number=1,
        reference=None,

        payer_name='NAVN',
    )

    assert record.to_ocr() == (
        'NY2121310000001NAVN                     '
        '                                   00000'
    )


def test_transaction_amount_item_2_cuts_too_long_payer_name():
    record = netsgiro.records.TransactionAmountItem2(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        transaction_type=(
            netsgiro.TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION),
        transaction_number=1,
        reference=None,

        payer_name='NAVN123456789',
    )

    assert record.to_ocr() == (
        'NY2121310000001NAVN123456               '
        '                                   00000'
    )


def test_transaction_amount_item_2_for_ocr_giro_transactions():
    record = netsgiro.records.TransactionAmountItem2(
        service_code=netsgiro.ServiceCode.OCR_GIRO,
        transaction_type=(
            netsgiro.TransactionType.FROM_GIRO_DEBITED_ACCOUNT),
        transaction_number=1,
        reference='099038562',

        form_number='9636827194',
        bank_date=date(1992, 1, 16),
        debit_account='99990512341',
    )

    assert record.to_ocr() == (
        'NY09103100000019636827194099038562000000'
        '0160192999905123410000000000000000000000'
    )


def test_transaction_amount_item_2_for_ocr_giro_without_bank_date():
    record = netsgiro.records.TransactionAmountItem2(
        service_code=netsgiro.ServiceCode.OCR_GIRO,
        transaction_type=(
            netsgiro.TransactionType.FROM_GIRO_DEBITED_ACCOUNT),
        transaction_number=1,
        reference='099038562',

        form_number='9636827194',
        bank_date=None,
        debit_account='99990512341',
    )

    assert record.to_ocr() == (
        'NY09103100000019636827194099038562000000'
        '0000000999905123410000000000000000000000'
    )


def test_transaction_amount_item_3_for_ocr_giro_transactions():
    record = netsgiro.records.TransactionAmountItem3(
        service_code=netsgiro.ServiceCode.OCR_GIRO,
        transaction_type=(
            netsgiro.TransactionType.PURCHASE_WITH_TEXT),
        transaction_number=1,
        text='Foo bar baz',
    )

    assert record.to_ocr() == (
        'NY0921320000001Foo bar baz              '
        '               0000000000000000000000000'
    )


def test_transaction_specification_for_avtalegiro_payment_request():
    record = netsgiro.records.TransactionSpecification(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        transaction_type=(
            netsgiro.TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION),
        transaction_number=1,
        line_number=1,
        column_number=1,
        text=' Gjelder Faktura: 168837  Dato: 19/03/04',
    )

    assert record.to_ocr() == (
        'NY212149000000140011 Gjelder Faktura: 16'
        '8837  Dato: 19/03/0400000000000000000000'
    )


def test_transaction_specification_from_longer_text():
    records = list(netsgiro.records.TransactionSpecification.from_text(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        transaction_type=(
            netsgiro.TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION),
        transaction_number=1,
        text=' Gjelder Faktura: 168837  Dato: 19/03/04\nFoo bar baz quux',
    ))

    assert len(records) == 4
    assert records[0].to_ocr() == (
        'NY212149000000140011 Gjelder Faktura: 16'
        '8837  Dato: 19/03/0400000000000000000000'
    )
    assert records[1].to_ocr() == (
        'NY212149000000140012                    '
        '                    00000000000000000000'
    )
    assert records[2].to_ocr() == (
        'NY212149000000140021Foo bar baz quux    '
        '                    00000000000000000000'
    )
    assert records[3].to_ocr() == (
        'NY212149000000140022                    '
        '                    00000000000000000000'
    )


def test_avtalegiro_agreement():
    record = netsgiro.records.AvtaleGiroAgreement(
        service_code=netsgiro.ServiceCode.AVTALEGIRO,
        transaction_type=(
            netsgiro.TransactionType.AVTALEGIRO_AGREEMENT),
        transaction_number=1,
        registration_type=(
            netsgiro.AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT),
        kid='008000011688373',
        notify=False,
    )

    assert record.to_ocr() == (
        'NY21947000000011          00800001168837'
        '3N00000000000000000000000000000000000000'
    )
