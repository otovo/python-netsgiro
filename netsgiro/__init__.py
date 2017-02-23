import re
from typing import List

import attr


__version__ = '0.1.0'


@attr.s
class Transmission:
    start_record = attr.ib()
    end_record = attr.ib()

    @classmethod
    def from_ocr(cls, lines: List[str]) -> 'Transmission':
        if len(lines) < 2:
            raise ValueError('Transmission must have at least two lines')

        for line in lines:
            if len(line) != 80:
                raise ValueError('All lines must be exactly 80 chars long')

        start_line, lines, end_line = lines[0], lines[1:-1], lines[-1]

        start_record = TransmissionStart.from_string(start_line)
        end_record = TransmissionEnd.from_string(end_line)

        return Transmission(
            start_record=start_record,
            end_record=end_record,
        )


@attr.s
class Record:
    service_code = attr.ib()
    transmission_type = attr.ib()
    record_type = attr.ib()

    _PATTERN = re.compile(r'^NY.{78}$')

    @classmethod
    def from_string(cls, line: str) -> 'Record':
        matches = re.match(cls._PATTERN, line)
        if matches is None:
            raise ValueError('Data did not match data format')
        return cls(**matches.groupdict())


@attr.s
class TransmissionStart(Record):
    data_transmitter = attr.ib()
    transmission_number = attr.ib()
    data_recipient = attr.ib()

    _PATTERN = re.compile(r'''
        ^
        NY      # Format code
        (?P<service_code>00)
        (?P<transmission_type>00)
        (?P<record_type>10)

        (?P<data_transmitter>\d{8})
        (?P<transmission_number>\d{7})
        (?P<data_recipient>\d{8})

        0{49}   # Padding
        $
    ''', re.VERBOSE)


@attr.s
class TransmissionEnd(Record):
    num_transactions = attr.ib()
    num_records = attr.ib()
    total_amount = attr.ib()
    nets_date = attr.ib()

    _PATTERN = re.compile(r'''
        ^
        NY      # Format code
        (?P<service_code>00)
        (?P<transmission_type>00)
        (?P<record_type>89)

        (?P<num_transactions>\d{8})
        (?P<num_records>\d{8})
        (?P<total_amount>\d{17})
        (?P<nets_date>\d{6})

        0{33}   # Filler
        $
    ''', re.VERBOSE)


def parse(data: str) -> Transmission:
    lines = data.strip().splitlines()
    return Transmission.from_ocr(lines)
