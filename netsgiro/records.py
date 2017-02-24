import datetime
import re
from typing import Optional, Union

import attr

from netsgiro.enums import RecordType, ServiceType


def to_date(value: Union[datetime.date, str]) -> Optional[datetime.date]:
    if isinstance(value, datetime.date):
        return value
    if value == '000000':
        return None
    return datetime.datetime.strptime(value, '%d%m%y').date()


def optional_str(value: str) -> Optional[str]:
    return value.strip() or None


@attr.s
class Record:
    service_code = attr.ib()
    record_type = attr.ib()

    _PATTERN = re.compile(r'^NY.{78}$')

    @classmethod
    def from_string(cls, line: str) -> 'Record':
        matches = cls._PATTERN.match(line)
        if matches is None:
            raise ValueError('Data did not match data format')
        return cls(**matches.groupdict())


@attr.s
class TransmissionStart(Record):
    RECORD_TYPE = RecordType.TRANSMISSION_START

    transmission_type = attr.ib()
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
    RECORD_TYPE = RecordType.TRANSMISSION_END

    transmission_type = attr.ib()
    num_transactions = attr.ib(convert=int)
    num_records = attr.ib(convert=int)
    total_amount = attr.ib(convert=int)
    nets_date = attr.ib(convert=to_date)

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


@attr.s
class AssignmentStart(Record):
    RECORD_TYPE = RecordType.ASSIGNMENT_START

    assignment_type = attr.ib()
    agreement_id = attr.ib()
    assignment_number = attr.ib()
    assignment_account = attr.ib()

    _PATTERN = re.compile(r'''
        ^
        NY      # Format code
        (?P<service_code>\d{2})
        (?P<assignment_type>00)
        (?P<record_type>20)

        (?P<agreement_id>\d{9})
        (?P<assignment_number>\d{7})
        (?P<assignment_account>\d{11})

        0{45}   # Filler
        $
    ''', re.VERBOSE)


@attr.s
class AssignmentEnd(Record):
    RECORD_TYPE = RecordType.ASSIGNMENT_END

    assignment_type = attr.ib()
    num_transactions = attr.ib(convert=int)
    num_records = attr.ib(convert=int)
    total_amount = attr.ib(convert=int)
    nets_date = attr.ib(convert=to_date)
    nets_date_earliest = attr.ib(convert=to_date)
    nets_date_latest = attr.ib(convert=to_date)

    _PATTERN = re.compile(r'''
        ^
        NY      # Format code
        (?P<service_code>\d{2})
        (?P<assignment_type>00)
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


@attr.s
class AvtaleGiroTransactionRecord(Record):
    transaction_type = attr.ib()
    transaction_number = attr.ib()


@attr.s
class AvtaleGiroAmountItem1(AvtaleGiroTransactionRecord):
    SERVICE_TYPE = ServiceType.AVTALEGIRO
    RECORD_TYPE = RecordType.TRANSACTION_AMOUNT_1

    due_date = attr.ib(convert=to_date)
    amount = attr.ib(convert=int)
    kid = attr.ib(convert=optional_str)

    _PATTERN = re.compile(r'''
        ^
        NY      # Format code
        (?P<service_code>21)
        (?P<transaction_type>\d{2})  # 02 or 21
        (?P<record_type>30)

        (?P<transaction_number>\d{7})
        (?P<due_date>\d{6})

        [ ]{11} # Filler

        (?P<amount>\d{17})
        (?P<kid>[\d ]{25})

        0{6}    # Filler
        $
    ''', re.VERBOSE)


@attr.s
class AvtaleGiroAmountItem2(AvtaleGiroTransactionRecord):
    SERVICE_TYPE = ServiceType.AVTALEGIRO
    RECORD_TYPE = RecordType.TRANSACTION_AMOUNT_2

    payer_name = attr.ib(convert=optional_str)  # TODO Better name?
    reference = attr.ib(convert=optional_str)   # TODO Better name?

    _PATTERN = re.compile(r'''
        ^
        NY      # Format code
        (?P<service_code>21)
        (?P<transaction_type>\d{2})  # 02 or 21
        (?P<record_type>31)

        (?P<transaction_number>\d{7})
        (?P<payer_name>.{10})

        [ ]{25} # Filler

        (?P<reference>.{25})

        0{5}    # Filler
        $
    ''', re.VERBOSE)


@attr.s
class AvtaleGiroSpecification(AvtaleGiroTransactionRecord):
    SERVICE_TYPE = ServiceType.AVTALEGIRO
    RECORD_TYPE = RecordType.TRANSACTION_SPECIFICATION

    line_number = attr.ib(convert=int)
    column_number = attr.ib(convert=int)
    text = attr.ib()

    _PATTERN = re.compile(r'''
        ^
        NY      # Format code
        (?P<service_code>21)
        (?P<transaction_type>21)
        (?P<record_type>49)

        (?P<transaction_number>\d{7})
        4       # Payment notification
        (?P<line_number>\d{3})
        (?P<column_number>\d{1})
        (?P<text>.{40})

        0{20}    # Filler
        $
    ''', re.VERBOSE)


def all_subclasses(cls):
    return cls.__subclasses__() + [
        subsubcls
        for subcls in cls.__subclasses__()
        for subsubcls in all_subclasses(subcls)]


RECORD_CLASSES = {
    cls.RECORD_TYPE: cls
    for cls in all_subclasses(Record)
    if getattr(cls, 'RECORD_TYPE', None)
}
