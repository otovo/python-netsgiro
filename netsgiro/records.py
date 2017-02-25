import datetime
import re
from typing import List, Optional, Union

import attr

import netsgiro


__all__ = [
    'TransmissionStart',
    'TransmissionEnd',
    'AssignmentStart',
    'AssignmentEnd',
    'AvtaleGiroAmountItem1',
    'AvtaleGiroAmountItem2',
    'AvtaleGiroSpecification',
    'AvtaleGiroAgreement',
    'get_records',
]


def to_service_code(
        value: Union[netsgiro.ServiceCode, int, str]) -> netsgiro.ServiceCode:
    return netsgiro.ServiceCode(int(value))


def to_record_type(
        value: Union[netsgiro.RecordType, int, str]) -> netsgiro.RecordType:
    return netsgiro.RecordType(int(value))


def to_assignment_type(
        value: Union[netsgiro.AvtaleGiroAssignmentType, int, str]
        ) -> netsgiro.AvtaleGiroAssignmentType:
    return netsgiro.AvtaleGiroAssignmentType(int(value))


def to_avtalegiro_transaction_type(
        value: Union[netsgiro.AvtaleGiroTransactionType, int, str]
        ) -> netsgiro.AvtaleGiroTransactionType:
    return netsgiro.AvtaleGiroTransactionType(int(value))


def to_avtalegiro_registration_type(
        value: Union[netsgiro.AvtaleGiroRegistrationType, int, str]
        ) -> netsgiro.AvtaleGiroRegistrationType:
    return netsgiro.AvtaleGiroRegistrationType(int(value))


def to_date(value: Union[datetime.date, str, None]) -> Optional[datetime.date]:
    if isinstance(value, datetime.date):
        return value
    if value == '000000' or value is None:
        return None
    return datetime.datetime.strptime(value, '%d%m%y').date()


def to_bool(value: Union[bool, str]) -> bool:
    if isinstance(value, bool):
        return value
    if value == 'J':
        return True
    elif value == 'N':
        return False
    else:
        raise ValueError("Expected 'J' or 'N', got {!r}".format(value))


def optional_int(value: Union[int, str, None]) -> Optional[int]:
    if value is None:
        return None
    else:
        return int(value)


def optional_str(value: str) -> Optional[str]:
    return value.strip() or None


@attr.s
class Record:
    service_code = attr.ib(convert=to_service_code)
    record_type = attr.ib(convert=to_record_type)

    _PATTERN = re.compile(r'^NY.{78}$')

    @classmethod
    def from_string(cls, line: str) -> 'Record':
        if hasattr(cls, '_PATTERNS'):
            record_subtype = int(line[4:6])
            if record_subtype not in cls._PATTERNS:
                raise ValueError(
                    'Unknown {} record subtype: {}'
                    .format(cls.__name__, record_subtype))
            pattern = cls._PATTERNS[record_subtype]
        else:
            pattern = cls._PATTERN

        matches = pattern.match(line)
        if matches is None:
            raise ValueError(
                '{!r} did not match {} record format'
                .format(line, cls.__name__))

        return cls(**matches.groupdict())


@attr.s
class TransmissionStart(Record):
    RECORD_TYPE = netsgiro.RecordType.TRANSMISSION_START

    transmission_type = attr.ib(convert=int)
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
    RECORD_TYPE = netsgiro.RecordType.TRANSMISSION_END

    transmission_type = attr.ib(convert=int)
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
    RECORD_TYPE = netsgiro.RecordType.ASSIGNMENT_START

    assignment_type = attr.ib(convert=to_assignment_type)
    assignment_number = attr.ib()
    assignment_account = attr.ib()

    # Only for assignment_type == 0
    agreement_id = attr.ib(default=None)

    _PATTERNS = {
        netsgiro.AvtaleGiroAssignmentType.PAYMENT_REQUESTS: re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>21)  # TODO: Verify if both 9 and 21?
            (?P<assignment_type>00)
            (?P<record_type>20)

            (?P<agreement_id>\d{9})
            (?P<assignment_number>\d{7})
            (?P<assignment_account>\d{11})

            0{45}   # Filler
            $
        ''', re.VERBOSE),
        netsgiro.AvtaleGiroAssignmentType.AGREEMENTS: re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>21)
            (?P<assignment_type>24)
            (?P<record_type>20)

            0{9}    # Filler

            (?P<assignment_number>\d{7})
            (?P<assignment_account>\d{11})

            0{45}   # Filler
            $
        ''', re.VERBOSE),
        netsgiro.AvtaleGiroAssignmentType.CANCELATIONS: re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>21)
            (?P<assignment_type>36)
            (?P<record_type>20)

            0{9}    # Filler

            (?P<assignment_number>\d{7})
            (?P<assignment_account>\d{11})

            0{45}   # Filler
            $
        ''', re.VERBOSE),
    }


@attr.s
class AssignmentEnd(Record):
    RECORD_TYPE = netsgiro.RecordType.ASSIGNMENT_END

    assignment_type = attr.ib(convert=to_assignment_type)
    num_transactions = attr.ib(convert=int)
    num_records = attr.ib(convert=int)

    # Only for assignment_type == 0
    total_amount = attr.ib(default=None, convert=optional_int)
    nets_date = attr.ib(default=None, convert=to_date)
    nets_date_earliest = attr.ib(default=None, convert=to_date)
    nets_date_latest = attr.ib(default=None, convert=to_date)

    _PATTERNS = {
        netsgiro.AvtaleGiroAssignmentType.PAYMENT_REQUESTS: re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>21)  # TODO: Verify if both 9 and 21?
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
        ''', re.VERBOSE),
        netsgiro.AvtaleGiroAssignmentType.AGREEMENTS: re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>21)
            (?P<assignment_type>24)
            (?P<record_type>88)

            (?P<num_transactions>\d{8})
            (?P<num_records>\d{8})

            0{56}   # Filler
            $
        ''', re.VERBOSE),
        netsgiro.AvtaleGiroAssignmentType.CANCELATIONS: re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>21)
            (?P<assignment_type>36)
            (?P<record_type>88)

            (?P<num_transactions>\d{8})
            (?P<num_records>\d{8})
            (?P<total_amount>\d{17})
            (?P<nets_date>\d{6})
            (?P<nets_date_earliest>\d{6})
            (?P<nets_date_latest>\d{6})

            0{21}   # Filler
            $
        ''', re.VERBOSE),
    }


@attr.s
class AvtaleGiroTransactionRecord(Record):
    transaction_type = attr.ib(convert=to_avtalegiro_transaction_type)
    transaction_number = attr.ib()


@attr.s
class AvtaleGiroAmountItem1(AvtaleGiroTransactionRecord):
    SERVICE_CODE = netsgiro.ServiceCode.AVTALEGIRO
    RECORD_TYPE = netsgiro.RecordType.TRANSACTION_AMOUNT_1

    due_date = attr.ib(convert=to_date)
    amount = attr.ib(convert=int)
    kid = attr.ib(convert=optional_str)

    _PATTERN = re.compile(r'''
        ^
        NY      # Format code
        (?P<service_code>21)
        (?P<transaction_type>\d{2})  # 02, 21, or 93
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
    SERVICE_CODE = netsgiro.ServiceCode.AVTALEGIRO
    RECORD_TYPE = netsgiro.RecordType.TRANSACTION_AMOUNT_2

    payer_name = attr.ib(convert=optional_str)  # TODO Better name?
    reference = attr.ib(convert=optional_str)   # TODO Better name?

    _PATTERN = re.compile(r'''
        ^
        NY      # Format code
        (?P<service_code>21)
        (?P<transaction_type>\d{2})  # 02, 21, or 93
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
    SERVICE_CODE = netsgiro.ServiceCode.AVTALEGIRO
    RECORD_TYPE = netsgiro.RecordType.TRANSACTION_SPECIFICATION

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


@attr.s
class AvtaleGiroAgreement(AvtaleGiroTransactionRecord):
    SERVICE_CODE = netsgiro.ServiceCode.AVTALEGIRO
    RECORD_TYPE = netsgiro.RecordType.TRANSACTION_AGREEMENTS

    registration_type = attr.ib(convert=to_avtalegiro_registration_type)
    kid = attr.ib(convert=optional_str)
    notify = attr.ib(convert=to_bool)

    _PATTERN = re.compile(r'''
        ^
        NY      # Format code
        (?P<service_code>21)
        (?P<transaction_type>94)
        (?P<record_type>70)

        (?P<transaction_number>\d{7})
        (?P<registration_type>\d{1})
        (?P<kid>[\d ]{25})
        (?P<notify>[JN]{1})

        0{38}   # Filler
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


def get_records(data: str) -> List[Record]:
    results = []

    for line in data.strip().splitlines():
        if len(line) != 80:
            raise ValueError('All lines must be exactly 80 chars long')

        record_type_str = line[6:8]
        if not record_type_str.isnumeric():
            raise ValueError(
                'Record type must be numeric, got {!r}'
                .format(record_type_str))

        record_type = netsgiro.RecordType(int(record_type_str))
        record_cls = RECORD_CLASSES[record_type]

        results.append(record_cls.from_string(line))

    return results
