from datetime import date
from decimal import Decimal

import netsgiro


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
    assert assignment.agreement_id == '000000000'
    assert assignment.number == '4000086'
    assert assignment.account == '88888888888'
    assert len(assignment.transactions) == 6

    transaction = assignment.transactions[0]

    assert isinstance(transaction, netsgiro.Transaction)
    assert transaction.service_code == netsgiro.ServiceCode.AVTALEGIRO
    assert transaction.type == (
        netsgiro.AvtaleGiroTransactionType.NOTIFICATION_FROM_BANK)
    assert transaction.number == '0000001'
    assert transaction.due_date == date(2004, 6, 17)
    assert transaction.amount == Decimal('1.00')
    assert transaction.amount_in_cents == 100
    assert transaction.kid == '008000011688373'
    assert transaction.payer_name == 'NAVN'
    assert transaction.reference is None
    assert transaction.specification_text == (
        ' Gjelder Faktura: 168837  Dato: 19/03/04'
        '                  ForfallsDato: 17/06/04\n'
    )
