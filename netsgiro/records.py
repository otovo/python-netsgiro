import re

import attr


@attr.s
class Record:
    service_code = attr.ib()
    subtype = attr.ib()
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

    @property
    def transmission_type(self):
        return self.subtype

    _PATTERN = re.compile(r'''
        ^
        NY      # Format code
        (?P<service_code>00)
        (?P<subtype>00)
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

    @property
    def transmission_type(self):
        return self.subtype

    _PATTERN = re.compile(r'''
        ^
        NY      # Format code
        (?P<service_code>00)
        (?P<subtype>00)
        (?P<record_type>89)

        (?P<num_transactions>\d{8})
        (?P<num_records>\d{8})
        (?P<total_amount>\d{17})
        (?P<nets_date>\d{6})

        0{33}   # Filler
        $
    ''', re.VERBOSE)


@attr.s
class AssignmentStart(Record):
    agreement_id = attr.ib()
    assignment_number = attr.ib()
    assignment_account = attr.ib()

    @property
    def assignment_type(self):
        return self.subtype

    _PATTERN = re.compile(r'''
        ^
        NY      # Format code
        (?P<service_code>\d{2})
        (?P<subtype>00)
        (?P<record_type>20)

        (?P<agreement_id>\d{9})
        (?P<assignment_number>\d{7})
        (?P<assignment_account>\d{11})

        0{45}   # Filler
        $
    ''', re.VERBOSE)


@attr.s
class AssignmentEnd(Record):
    num_transactions = attr.ib()
    num_records = attr.ib()
    total_amount = attr.ib()
    nets_date = attr.ib()
    nets_date_earliest = attr.ib()
    nets_date_latest = attr.ib()

    @property
    def assignment_type(self):
        return self.subtype

    _PATTERN = re.compile(r'''
        ^
        NY      # Format code
        (?P<service_code>\d{2})
        (?P<subtype>00)
        (?P<record_type>88)

        (?P<num_transactions>\d{8})
        (?P<num_records>\d{8})
        (?P<total_amount>\d{17})
        (?P<nets_date>\d{6})
        (?P<nets_date_earliest>\d{6})
        (?P<nets_date_latest>\d{6})

        0{21}   # Filler
        $
    ''', re.VERBOSE)
