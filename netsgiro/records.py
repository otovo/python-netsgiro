import datetime
import re
from typing import List, Optional, Union

import attr
from attr.validators import instance_of, optional

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
        value: Union[netsgiro.AssignmentType, int, str]
        ) -> netsgiro.AssignmentType:
    return netsgiro.AssignmentType(int(value))


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


def str_of_length(length):
    def validator(instance, attribute, value):
        instance_of(str)(instance, attribute, value)
        if len(value) != length:
            raise ValueError(
                '{0.name} must be exactly {1} chars, got {2!r}'
                .format(attribute, length, value))
    return validator


@attr.s
class Record:
    service_code = attr.ib(convert=to_service_code)

    _PATTERNS = []

    @classmethod
    def from_string(cls, line: str) -> 'Record':
        """Parse OCR string into a record object."""

        for pattern in cls._PATTERNS:
            matches = pattern.match(line)
            if matches is not None:
                return cls(**matches.groupdict())

        raise ValueError(
            '{!r} did not match {} record formats'
            .format(line, cls.__name__))

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        raise NotImplementedError


@attr.s
class TransmissionStart(Record):
    transmission_number = attr.ib(validator=str_of_length(7))
    data_transmitter = attr.ib(validator=str_of_length(8))
    data_recipient = attr.ib(validator=str_of_length(8))

    _RECORD_TYPE = netsgiro.RecordType.TRANSMISSION_START
    record_type = attr.ib(
        init=False, default=_RECORD_TYPE, convert=to_record_type)

    _PATTERNS = [
        re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>00)
            00      # Transmission type, always 00
            10      # Record type

            (?P<data_transmitter>\d{8})
            (?P<transmission_number>\d{7})
            (?P<data_recipient>\d{8})

            0{49}   # Padding
            $
        ''', re.VERBOSE),
    ]

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        return (
            'NY000010'
            '{self.data_transmitter:8}'
            '{self.transmission_number:7}'
            '{self.data_recipient:8}'
            + ('0' * 49)
        ).format(self=self)


@attr.s
class TransmissionEnd(Record):
    num_transactions = attr.ib(convert=int)
    num_records = attr.ib(convert=int)
    total_amount = attr.ib(convert=int)
    nets_date = attr.ib(convert=to_date)

    _RECORD_TYPE = netsgiro.RecordType.TRANSMISSION_END
    record_type = attr.ib(
        init=False, default=_RECORD_TYPE, convert=to_record_type)

    _PATTERNS = [
        re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>00)
            00      # Transmission type, always 00
            89      # Record type

            (?P<num_transactions>\d{8})
            (?P<num_records>\d{8})
            (?P<total_amount>\d{17})
            (?P<nets_date>\d{6})

            0{33}   # Filler
            $
        ''', re.VERBOSE),
    ]

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        return (
            'NY000089'
            '{self.num_transactions:08d}'
            '{self.num_records:08d}'
            '{self.total_amount:017d}'
            '{self.nets_date:%d%m%y}'
            + ('0' * 33)
        ).format(self=self)


@attr.s
class AssignmentStart(Record):
    assignment_type = attr.ib(convert=to_assignment_type)
    assignment_number = attr.ib(validator=str_of_length(7))
    assignment_account = attr.ib(validator=str_of_length(11))

    # Only for assignment_type == AssignmentType.TRANSACTIONS
    agreement_id = attr.ib(default=None, validator=optional(str_of_length(9)))

    _RECORD_TYPE = netsgiro.RecordType.ASSIGNMENT_START
    record_type = attr.ib(
        init=False, default=_RECORD_TYPE, convert=to_record_type)

    _PATTERNS = [
        re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>(09|21))
            (?P<assignment_type>00)
            20      # Record type

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
            20      # Record type

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
            20      # Record type

            0{9}    # Filler

            (?P<assignment_number>\d{7})
            (?P<assignment_account>\d{11})

            0{45}   # Filler
            $
        ''', re.VERBOSE),
    ]

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        return (
            'NY'
            '{self.service_code:02d}'
            '{self.assignment_type:02d}'
            '20'
            + (self.agreement_id and '{self.agreement_id:9}' or ('0' * 9)) +
            '{self.assignment_number:7}'
            '{self.assignment_account:11}'
            + ('0' * 45)
        ).format(self=self)


@attr.s
class AssignmentEnd(Record):
    assignment_type = attr.ib(convert=to_assignment_type)
    num_transactions = attr.ib(convert=int)
    num_records = attr.ib(convert=int)

    # Only for transactions and cancellations
    total_amount = attr.ib(default=None, convert=optional_int)
    nets_date_1 = attr.ib(default=None, convert=to_date)
    nets_date_2 = attr.ib(default=None, convert=to_date)
    nets_date_3 = attr.ib(default=None, convert=to_date)

    _RECORD_TYPE = netsgiro.RecordType.ASSIGNMENT_END
    record_type = attr.ib(
        init=False, default=_RECORD_TYPE, convert=to_record_type)

    _PATTERNS = [
        re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>(09|21))
            (?P<assignment_type>00)     # Transactions / payment requests
            88      # Record type

            (?P<num_transactions>\d{8})
            (?P<num_records>\d{8})
            (?P<total_amount>\d{17})
            (?P<nets_date_1>\d{6})
            (?P<nets_date_2>\d{6})
            (?P<nets_date_3>\d{6})

            0{21}   # Filler
            $
        ''', re.VERBOSE),
        re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>21)
            (?P<assignment_type>24)     # AvtaleGiro agreements
            88      # Record type

            (?P<num_transactions>\d{8})
            (?P<num_records>\d{8})

            0{56}   # Filler
            $
        ''', re.VERBOSE),
        re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>21)
            (?P<assignment_type>36)     # AvtaleGiro cancellations
            88      # Record type

            (?P<num_transactions>\d{8})
            (?P<num_records>\d{8})
            (?P<total_amount>\d{17})
            (?P<nets_date_1>\d{6})
            (?P<nets_date_2>\d{6})

            0{27}   # Filler
            $
        ''', re.VERBOSE),
    ]

    @property
    def nets_date(self):
        if self.service_code == netsgiro.ServiceCode.OCR_GIRO:
            return self.nets_date_1
        else:
            raise ValueError(
                'Unhandled service code: {}'.format(self.service_code))

    @property
    def nets_date_earliest(self):
        if self.service_code == netsgiro.ServiceCode.OCR_GIRO:
            return self.nets_date_2
        elif self.service_code == netsgiro.ServiceCode.AVTALEGIRO:
            return self.nets_date_1
        else:
            raise ValueError(
                'Unhandled service code: {}'.format(self.service_code))

    @property
    def nets_date_latest(self):
        if self.service_code == netsgiro.ServiceCode.OCR_GIRO:
            return self.nets_date_3
        elif self.service_code == netsgiro.ServiceCode.AVTALEGIRO:
            return self.nets_date_2
        else:
            raise ValueError(
                'Unhandled service code: {}'.format(self.service_code))

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        return (
            'NY'
            '{self.service_code:02d}'
            '{self.assignment_type:02d}'
            '88'
            '{self.num_transactions:08d}'
            '{self.num_records:08d}'
            + (self.total_amount and '{self.total_amount:017d}' or ('0' * 17))
            + (self.nets_date_1 and '{self.nets_date_1:%d%m%y}' or ('0' * 6))
            + (self.nets_date_2 and '{self.nets_date_2:%d%m%y}' or ('0' * 6))
            + (self.nets_date_3 and '{self.nets_date_3:%d%m%y}' or ('0' * 6))
            + ('0' * 21)
        ).format(self=self)


@attr.s
class TransactionRecord(Record):
    transaction_type = attr.ib(convert=to_transaction_type)
    transaction_number = attr.ib(convert=int)


@attr.s
class TransactionAmountItem1(TransactionRecord):
    nets_date = attr.ib(convert=to_date)
    amount = attr.ib(convert=int)
    kid = attr.ib(convert=optional_str)

    # Only OCR Giro
    centre_id = attr.ib(default=None, validator=optional(str_of_length(2)))
    day_code = attr.ib(default=None, convert=optional_int)
    partial_settlement_number = attr.ib(default=None, convert=optional_int)
    partial_settlement_serial_number = attr.ib(
        default=None, validator=optional(str_of_length(5)))
    sign = attr.ib(default=None, validator=optional(str_of_length(1)))

    _RECORD_TYPE = netsgiro.RecordType.TRANSACTION_AMOUNT_ITEM_1
    record_type = attr.ib(
        init=False, default=_RECORD_TYPE, convert=to_record_type)

    _PATTERNS = [
        re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>09)
            (?P<transaction_type>\d{2})  # 10-21
            30      # Record type

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
            30      # Record type

            (?P<transaction_number>\d{7})
            (?P<nets_date>\d{6})

            [ ]{11} # Filler

            (?P<amount>\d{17})
            (?P<kid>[\d ]{25})

            0{6}    # Filler
            $
        ''', re.VERBOSE),
    ]

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        if self.service_code == netsgiro.ServiceCode.OCR_GIRO:
            ocr_giro_fields = (
                '{self.centre_id:2}'
                '{self.day_code:02d}'
                '{self.partial_settlement_number:01d}'
                '{self.partial_settlement_serial_number:5}'
                '{self.sign:1}'
            ).format(self=self)
        else:
            ocr_giro_fields = ' ' * 11

        return (
            'NY'
            '{self.service_code:02d}'
            '{self.transaction_type:02d}'
            '30'
            '{self.transaction_number:07d}'
            '{self.nets_date:%d%m%y}'
            + ocr_giro_fields +
            '{self.amount:017d}'
            '{self.kid:>25}'
            + ('0' * 6)
        ).format(self=self)


@attr.s
class TransactionAmountItem2(TransactionRecord):
    reference = attr.ib(convert=optional_str)

    # Only OCR Giro
    form_number = attr.ib(default=None, validator=optional(str_of_length(10)))
    bank_date = attr.ib(default=None, convert=to_date)
    debit_account = attr.ib(
        default=None, validator=optional(str_of_length(11)))

    # Only AvtaleGiro
    payer_name = attr.ib(default=None, convert=optional_str)

    # TODO Add accessors to parts of reference depending on transaction_type

    _RECORD_TYPE = netsgiro.RecordType.TRANSACTION_AMOUNT_ITEM_2
    record_type = attr.ib(
        init=False, default=_RECORD_TYPE, convert=to_record_type)

    _PATTERNS = [
        re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>09)
            (?P<transaction_type>\d{2})  # 10-21
            31      # Record type

            (?P<transaction_number>\d{7})
            (?P<form_number>\d{10})
            (?P<reference>\d{9})

            .{7} # Filler   # XXX Not always filled with zero in test data

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
            31      # Record type

            (?P<transaction_number>\d{7})
            (?P<payer_name>.{10})

            [ ]{25} # Filler

            (?P<reference>.{25})

            0{5}    # Filler
            $
        ''', re.VERBOSE),
    ]

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        common_fields = (
            'NY'
            '{self.service_code:02d}'
            '{self.transaction_type:02d}'
            '31'
            '{self.transaction_number:07d}'
        ).format(self=self)

        if self.service_code == netsgiro.ServiceCode.OCR_GIRO:
            service_fields = (
                '{self.form_number:10}'
                + (self.reference and '{self.reference:9}' or (' ' * 9))
                + ('0' * 7) +
                '{self.bank_date:%d%m%y}'
                '{self.debit_account:11}'
                + ('0' * 22)
            ).format(self=self)
        elif self.service_code == netsgiro.ServiceCode.AVTALEGIRO:
            service_fields = (
                '{self.payer_name:10}'
                + (' ' * 25)
                + (self.reference and '{self.reference:25}' or (' ' * 25))
                + ('0' * 5)
            ).format(self=self)
        else:
            service_fields = ' ' * 35

        return common_fields + service_fields


@attr.s
class TransactionAmountItem3(TransactionRecord):
    text = attr.ib(convert=optional_str)

    _RECORD_TYPE = netsgiro.RecordType.TRANSACTION_AMOUNT_ITEM_3
    record_type = attr.ib(
        init=False, default=_RECORD_TYPE, convert=to_record_type)

    _PATTERNS = [
        re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>09)
            (?P<transaction_type>\d{2})  # 20-21
            32      # Record type

            (?P<transaction_number>\d{7})
            (?P<text>.{40})

            0{25}    # Filler
            $
        ''', re.VERBOSE),
    ]

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        return (
            'NY09'
            '{self.transaction_type:02d}'
            '32'
            '{self.transaction_number:07d}'
            '{self.text:40}'
            + ('0' * 25)
        ).format(self=self)


@attr.s
class TransactionSpecification(TransactionRecord):
    line_number = attr.ib(convert=int)
    column_number = attr.ib(convert=int)
    text = attr.ib(validator=instance_of(str))

    _RECORD_TYPE = netsgiro.RecordType.TRANSACTION_SPECIFICATION
    record_type = attr.ib(
        init=False, default=_RECORD_TYPE, convert=to_record_type)

    _PATTERNS = [
        re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>21)
            (?P<transaction_type>21)
            49      # Record type

            (?P<transaction_number>\d{7})
            4       # Payment notification
            (?P<line_number>\d{3})
            (?P<column_number>\d{1})
            (?P<text>.{40})

            0{20}    # Filler
            $
        ''', re.VERBOSE),
    ]

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        return (
            'NY212149'
            '{self.transaction_number:07d}'
            '4'
            '{self.line_number:03d}'
            '{self.column_number:01d}'
            '{self.text:40}'
            + ('0' * 20)
        ).format(self=self)


@attr.s
class AvtaleGiroAgreement(TransactionRecord):
    registration_type = attr.ib(convert=to_avtalegiro_registration_type)
    kid = attr.ib(convert=optional_str)
    notify = attr.ib(convert=to_bool)

    _RECORD_TYPE = netsgiro.RecordType.TRANSACTION_AGREEMENTS
    record_type = attr.ib(
        init=False, default=_RECORD_TYPE, convert=to_record_type)

    _PATTERNS = [
        re.compile(r'''
            ^
            NY      # Format code
            (?P<service_code>21)
            (?P<transaction_type>94)
            70      # Record type

            (?P<transaction_number>\d{7})
            (?P<registration_type>\d{1})
            (?P<kid>[\d ]{25})
            (?P<notify>[JN]{1})

            0{38}   # Filler
            $
        ''', re.VERBOSE),
    ]

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        return (
            'NY219470'
            '{self.transaction_number:07d}'
            '{self.registration_type:01d}'
            '{self.kid:>25}'
            + (self.notify and 'J' or 'N')
            + ('0' * 38)
        ).format(self=self)


def get_records(data: str) -> List[Record]:
    """Parses an OCR file into a list of record objects.

    Example::

        >>> netsgiro.get_records(data)
        [
            TransmissionStart(service_code=<ServiceCode.NONE: 0>,
                record_type=<RecordType.TRANSMISSION_START: 10>,
                data_transmitter='55555555', transmission_number='1000081',
                data_recipient='00008080'),
            AssignmentStart(service_code=<ServiceCode.AVTALEGIRO: 21>,
                record_type=<RecordType.ASSIGNMENT_START:20>,
                assignment_type=<AssignmentType.TRANSACTIONS: 0>,
                assignment_number='4000086', assignment_account='88888888888',
                agreement_id='000000000'),
            TransactionAmountItem1(service_code=<ServiceCode.AVTALEGIRO: 21>,
                record_type=<RecordType.TRANSACTION_AMOUNT_ITEM_1: 30>,
                transaction_type=<TransactionType.PURCHASE_WITH_TEXT: 21>,
                transaction_number=1, nets_date=datetime.date(2004, 6,
                17), amount=100, kid='008000011688373', centre_id=None,
                day_code=None, partial_settlement_number=None,
                partial_settlement_serial_number=None, sign=None),
            ...
            TransmissionEnd(service_code=<ServiceCode.NONE: 0>,
                record_type=<RecordType.TRANSMISSION_END: 89>,
                num_transactions=6, num_records=22, total_amount=600,
                nets_date=datetime.date(2004, 6, 17))
        ]
    """

    def all_subclasses(cls):
        return cls.__subclasses__() + [
            subsubcls
            for subcls in cls.__subclasses__()
            for subsubcls in all_subclasses(subcls)]

    record_classes = {
        cls._RECORD_TYPE: cls
        for cls in all_subclasses(Record)
        if hasattr(cls, '_RECORD_TYPE')
    }

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
        record_cls = record_classes[record_type]

        results.append(record_cls.from_string(line))

    return results
