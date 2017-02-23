from pathlib import Path

import pytest

import netsgiro


TEST_DIR = Path(__file__).parent


@pytest.fixture
def payment_request_data():
    filepath = TEST_DIR / 'data' / 'avtalegiro_payment_request.txt'
    with filepath.open('r', encoding='iso-8859-1') as fh:
        return fh.read()


def test_transmission_with_invalid_start_record():
    with pytest.raises(ValueError) as exc_info:
        netsgiro.Transmission.from_ocr([
            'XX' + ('0' * 78),
            'NY00008900000006000000220000000000000060'
            '0170604000000000000000000000000000000000',
        ])

    assert 'not match data format' in str(exc_info)


def test_with_invalid_end_record():
    with pytest.raises(ValueError) as exc_info:
        netsgiro.Transmission.from_ocr([
            'NY00001055555555100008100008080000000000'
            '0000000000000000000000000000000000000000',
            'XX' + ('0' * 78),
        ])

    assert 'not match data format' in str(exc_info)


def test_empty_transmission():
    transmission = netsgiro.Transmission.from_ocr([
        'NY00001055555555100008100008080000000000'
        '0000000000000000000000000000000000000000',
        'NY00008900000006000000220000000000000060'
        '0170604000000000000000000000000000000000',
    ])

    assert isinstance(transmission, netsgiro.Transmission)

    assert transmission.start_record.service_code == '00'
    assert transmission.start_record.transmission_type == '00'
    assert transmission.start_record.record_type == '10'
    assert transmission.start_record.data_transmitter == '55555555'
    assert transmission.start_record.transmission_number == '1000081'
    assert transmission.start_record.data_recipient == '00008080'

    assert transmission.end_record.service_code == '00'
    assert transmission.end_record.transmission_type == '00'
    assert transmission.end_record.num_transactions == '00000006'
    assert transmission.end_record.num_records == '00000022'
    assert transmission.end_record.total_amount == '00000000000000600'
    assert transmission.end_record.nets_date == '170604'

    assert transmission.contents is None


def test_empty_assignment():
    assignment = netsgiro.Assignment.from_ocr([
        'NY21002000000000040000868888888888800000'
        '0000000000000000000000000000000000000000',
        'NY21008800000006000000200000000000000060'
        '0170604170604000000000000000000000000000',
    ])

    assert isinstance(assignment, netsgiro.Assignment)

    assert assignment.start_record.service_code == '21'
    assert assignment.start_record.assignment_type == '00'
    assert assignment.start_record.record_type == '20'
    assert assignment.start_record.agreement_id == '000000000'
    assert assignment.start_record.assignment_number == '4000086'
    assert assignment.start_record.assignment_account == '88888888888'

    assert assignment.end_record.service_code == '21'
    assert assignment.end_record.assignment_type == '00'
    assert assignment.end_record.record_type == '88'
    assert assignment.end_record.num_transactions == '00000006'
    assert assignment.end_record.num_records == '00000020'
    assert assignment.end_record.total_amount == '00000000000000600'
    assert assignment.end_record.nets_date == '170604'
    assert assignment.end_record.nets_date_earliest == '170604'
    assert assignment.end_record.nets_date_latest == '000000'


def test_parse_empty_string_fails():
    with pytest.raises(ValueError) as exc_info:
        netsgiro.parse('')

    assert 'at least two lines' in str(exc_info)


def test_parse_too_short_lines_fails():
    with pytest.raises(ValueError) as exc_info:
        netsgiro.parse(
            'NY0000\n'
            'NY0000\n'
        )

    assert 'exactly 80 chars long' in str(exc_info)


def test_parse_payment_request(payment_request_data):
    transmission = netsgiro.parse(payment_request_data)

    assert isinstance(transmission, netsgiro.Transmission)
