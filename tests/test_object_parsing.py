from datetime import date
from decimal import Decimal

import netsgiro


def test_parse_agreements(agreements_data):
    transmission = netsgiro.parse(agreements_data)

    assert isinstance(transmission, netsgiro.Transmission)
    assert transmission.number == '1091949'
    assert transmission.data_transmitter == netsgiro.NETS_ID
    assert transmission.data_recipient == '00010200'
    assert transmission.date == date(2017, 4, 19)
    assert len(transmission.assignments) == 1

    assignment = transmission.assignments[0]

    assert isinstance(assignment, netsgiro.Assignment)
    assert assignment.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert assignment.type == netsgiro.AssignmentType.AVTALEGIRO_AGREEMENTS
    assert assignment.agreement_id is None
    assert assignment.number == '0000002'
    assert assignment.account == '99991042764'
    assert len(assignment.transactions) == 16

    agreement_1 = assignment.transactions[0]

    assert isinstance(agreement_1, netsgiro.Agreement)
    assert agreement_1.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert agreement_1.TRANSACTION_TYPE == (
        netsgiro.TransactionType.AVTALEGIRO_AGREEMENT)
    assert agreement_1.number == 1

    assert agreement_1.registration_type == (
        netsgiro.AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT)
    assert agreement_1.kid == '000112000507155'
    assert agreement_1.notify is True

    agreement_2 = assignment.transactions[1]

    assert isinstance(agreement_2, netsgiro.Agreement)
    assert agreement_2.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert agreement_2.TRANSACTION_TYPE == (
        netsgiro.TransactionType.AVTALEGIRO_AGREEMENT)
    assert agreement_2.number == 2

    assert agreement_2.registration_type == (
        netsgiro.AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT)
    assert agreement_2.kid == '001006300507304'
    assert agreement_2.notify is False


def test_parse_payment_request(payment_request_data):
    transmission = netsgiro.parse(payment_request_data)

    assert isinstance(transmission, netsgiro.Transmission)
    assert transmission.number == '1000081'
    assert transmission.data_transmitter == '55555555'
    assert transmission.data_recipient == netsgiro.NETS_ID
    assert transmission.date == date(2004, 6, 17)
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

    assert isinstance(transaction, netsgiro.PaymentRequest)
    assert transaction.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert transaction.type == (
        netsgiro.TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION)
    assert transaction.number == 1
    assert transaction.date == date(2004, 6, 17)
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
    assert transmission.date == date(1992, 1, 20)
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
        netsgiro.TransactionType.PURCHASE_WITH_TEXT)
    assert transaction.number == 1
    assert transaction.date == date(1992, 1, 20)
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
