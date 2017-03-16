from datetime import date

import pytest

import netsgiro


def test_transmission_start():
    record = netsgiro.TransmissionStart(
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
        netsgiro.TransmissionStart(
            service_code=netsgiro.ServiceCode.NONE,
            transmission_number=transmission_number,
            data_transmitter=data_transmitter,
            data_recipient=data_recipient,
        )


def test_transmission_end():
    record = netsgiro.TransmissionEnd(
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
        netsgiro.TransmissionEnd(
            service_code=netsgiro.ServiceCode.NONE,
            num_transactions=num_tx,
            num_records=num_records,
            total_amount=total_amount,
            nets_date=nets_date,
        )
