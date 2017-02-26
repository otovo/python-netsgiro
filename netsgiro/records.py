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
    'TransactionAmountItem1',
    'TransactionAmountItem2',
    'TransactionAmountItem3',
    'TransactionSpecification',
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


def to_transaction_type(
        value: Union[netsgiro.TransactionType, int, str]
        ) -> netsgiro.TransactionType:
    return netsgiro.TransactionType(int(value))


def to_avtalegiro_registration_type(
        value: Union[netsgiro.AvtaleGiroRegistrationType, int, str]
        ) -> netsgiro.AvtaleGiroRegistrationType:
    return netsgiro.AvtaleGiroRegistrationType(int(value))


def to_date(value: Union[datetime.date, str, None]) -> Optional[datetime.date]:
    if isinstance(value, datetime.date):
        return value
    if value is None or value == '000000':
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


def optional_str(value: Optional[str]) -> Optional[str]:
    return value and value.strip() or None


@attr.s
class Record:
    service_code = attr.ib(convert=to_service_code)
    record_type = attr.ib(convert=to_record_type)

    _PATTERN = re.compile(r'^NY.{78}$')

    @classmethod
    def from_string(cls, line: str) -> 'Record':
        if hasattr(cls, '_PATTERNS'):
            patterns = cls._PATTERNS
        else:
            patterns = [cls._PATTERN]

        for pattern in patterns:
            matches = pattern.match(line)
            if matches is not None:
                return cls(**matches.groupdict())

        raise ValueError(
            '{!r} did not match {} record formats'
            .format(line, cls.__name__))


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

    _PATTERNS = [
        re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>(09|21))
            (?P<assignment_type>00)
            (?P<record_type>20)

            (?P<agreement_id>\d{9})
            (?P<assignment_number>\d{7})
            (?P<assignment_account>\d{11})

            0{45}   # Filler
            $
        ''', re.VERBOSE),
        re.compile(r'''
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
        re.compile(r'''
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
    ]


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

    _PATTERNS = [
        re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>(09|21))
            (?P<assignment_type>00)     # Payment requests
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
        re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>21)
            (?P<assignment_type>24)     # Agreements
            (?P<record_type>88)

            (?P<num_transactions>\d{8})
            (?P<num_records>\d{8})

            0{56}   # Filler
            $
        ''', re.VERBOSE),
        re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>21)
            (?P<assignment_type>36)     # Cancelations
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
    ]


@attr.s
class TransactionRecord(Record):
    transaction_type = attr.ib(convert=to_transaction_type)
    transaction_number = attr.ib()


@attr.s
class TransactionAmountItem1(TransactionRecord):
    RECORD_TYPE = netsgiro.RecordType.TRANSACTION_AMOUNT_1

    nets_date = attr.ib(convert=to_date)
    amount = attr.ib(convert=int)
    kid = attr.ib(convert=optional_str)

    # Only OCR Giro
    centre_id = attr.ib(default=None)
    day_code = attr.ib(default=None, convert=optional_int)
    partial_settlement_number = attr.ib(default=None, convert=optional_int)
    partial_settlement_serial_number = attr.ib(default=None)
    sign = attr.ib(default=None)

    _PATTERNS = [
        re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>09)
            (?P<transaction_type>\d{2})  # 10-21
            (?P<record_type>30)

            (?P<transaction_number>\d{7})
            (?P<nets_date>\d{6})

            (?P<centre_id>\d{2})
            (?P<day_code>\d{2})
            (?P<partial_settlement_number>\d{1})
            (?P<partial_settlement_serial_number>\d{5})
            (?P<sign>[-0]{1})

            (?P<amount>\d{17})
            (?P<kid>[\d ]{25})

            0{6}    # Filler
            $
        ''', re.VERBOSE),
        re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>21)
            (?P<transaction_type>\d{2})  # 02, 21, or 93
            (?P<record_type>30)

            (?P<transaction_number>\d{7})
            (?P<nets_date>\d{6})

            [ ]{11} # Filler

            (?P<amount>\d{17})
            (?P<kid>[\d ]{25})

            0{6}    # Filler
            $
        ''', re.VERBOSE),
    ]


@attr.s
class TransactionAmountItem2(TransactionRecord):
    RECORD_TYPE = netsgiro.RecordType.TRANSACTION_AMOUNT_2

    reference = attr.ib(convert=optional_str)

    # Only OCR Giro
    form_number = attr.ib(default=None)
    bank_date = attr.ib(default=None, convert=to_date)
    debit_account = attr.ib(default=None)

    # Only AvtaleGiro
    payer_name = attr.ib(default=None, convert=optional_str)

    # TODO Add accessors to parts of reference depending on transaction_type

    _PATTERNS = [
        re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>09)
            (?P<transaction_type>\d{2})  # 10-21
            (?P<record_type>31)

            (?P<transaction_number>\d{7})
            (?P<form_number>\d{10})
            (?P<reference>\d{9})

            .{7} # Filler   # TODO Not always zero in test data

            (?P<bank_date>\d{6})
            (?P<debit_account>\d{11})

            0{22}    # Filler
            $
        ''', re.VERBOSE),
        re.compile(r'''
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
        ''', re.VERBOSE),
    ]


@attr.s
class TransactionAmountItem3(TransactionRecord):
    RECORD_TYPE = netsgiro.RecordType.TRANSACTION_AMOUNT_3

    text = attr.ib(convert=optional_str)

    _PATTERN = re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>09)
            (?P<transaction_type>\d{2})  # 20-21
            (?P<record_type>32)

            (?P<transaction_number>\d{7})
            (?P<text>.{40})

            0{25}    # Filler
            $
    ''', re.VERBOSE)


@attr.s
class TransactionSpecification(TransactionRecord):
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
class AvtaleGiroAgreement(TransactionRecord):
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
