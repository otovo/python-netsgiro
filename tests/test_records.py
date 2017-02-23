from netsgiro import records


def test_transmission_start():
    record = records.TransmissionStart.from_string(
        'NY00001055555555100008100008080000000000'
        '0000000000000000000000000000000000000000'
    )

    assert record.service_code == '00'
    assert record.transmission_type == '00'
    assert record.record_type == '10'

    assert record.data_transmitter == '55555555'
    assert record.transmission_number == '1000081'
    assert record.data_recipient == '00008080'


def test_transmission_end():
    record = records.TransmissionEnd.from_string(
        'NY00008900000006000000220000000000000060'
        '0170604000000000000000000000000000000000'
    )

    assert record.service_code == '00'
    assert record.transmission_type == '00'
    assert record.record_type == '89'

    assert record.num_transactions == '00000006'
    assert record.num_records == '00000022'
    assert record.total_amount == '00000000000000600'
    assert record.nets_date == '170604'


def test_assignment_start():
    record = records.AssignmentStart.from_string(
        'NY21002000000000040000868888888888800000'
        '0000000000000000000000000000000000000000'
    )

    assert record.service_code == '21'
    assert record.assignment_type == '00'
    assert record.record_type == '20'

    assert record.agreement_id == '000000000'
    assert record.assignment_number == '4000086'
    assert record.assignment_account == '88888888888'


def test_assignment_end():
    record = records.AssignmentEnd.from_string(
        'NY21008800000006000000200000000000000060'
        '0170604170604000000000000000000000000000'
    )

    assert record.service_code == '21'
    assert record.assignment_type == '00'
    assert record.record_type == '88'

    assert record.num_transactions == '00000006'
    assert record.num_records == '00000020'
    assert record.total_amount == '00000000000000600'
    assert record.nets_date == '170604'
    assert record.nets_date_earliest == '170604'
    assert record.nets_date_latest == '000000'


def test_avtalegiro_amount_item_1():
    record = records.AvtaleGiroAmountItem1.from_string(
        'NY2121300000001170604           00000000'
        '000000100          008000011688373000000'
    )

    assert record.service_code == '21'
    assert record.transaction_type == '21'
    assert record.record_type == '30'

    assert record.transaction_number == '0000001'
    assert record.due_date == '170604'
    assert record.amount == '00000000000000100'
    assert record.kid == '          008000011688373'


def test_avtalegiro_amount_item_2():
    record = records.AvtaleGiroAmountItem2.from_string(
        'NY2121310000001NAVN                     '
        '                                   00000'
    )

    assert record.service_code == '21'
    assert record.transaction_type == '21'
    assert record.record_type == '31'

    assert record.transaction_number == '0000001'
    assert record.payer_name == 'NAVN      '
    assert record.reference == ' ' * 25


def test_avtalegiro_specification():
    record = records.AvtaleGiroSpecification.from_string(
        'NY212149000000140011 Gjelder Faktura: 16'
        '8837  Dato: 19/03/0400000000000000000000'
    )

    assert record.service_code == '21'
    assert record.transaction_type == '21'
    assert record.record_type == '49'

    assert record.transaction_number == '0000001'
    assert record.line_number == '001'
    assert record.column_number == '1'
    assert record.text == ' Gjelder Faktura: 168837  Dato: 19/03/04'
