"""The lower-level records API."""

import datetime
import re
from typing import Iterable, List, Optional, Sequence, Tuple, Union

import attr
from attr.validators import optional

import netsgiro
from netsgiro.converters import (
    fixed_len_str,
    stripped_newlines,
    stripped_spaces_around,
    truthy_or_none,
    value_or_none,
)
from netsgiro.validators import str_of_length, str_of_max_length

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
    'parse',
]


def to_service_code(
    value: Union[netsgiro.ServiceCode, int, str]
) -> netsgiro.ServiceCode:
    return netsgiro.ServiceCode(int(value))


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
        raise ValueError(f"Expected 'J' or 'N', got {value!r}")


to_safe_str_or_none = value_or_none(
    stripped_newlines(stripped_spaces_around(truthy_or_none(str)))
)


@attr.s
class Record:
    service_code = attr.ib(converter=to_service_code)

    _PATTERNS = []

    @classmethod
    def from_string(cls, line: str) -> 'Record':
        """Parse OCR string into a record object."""

        for pattern in cls._PATTERNS:
            matches = pattern.match(line)
            if matches is not None:
                return cls(**matches.groupdict())

        raise ValueError(
            f'{line!r} did not match {cls.__name__} record formats'
        )

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        raise NotImplementedError


@attr.s
class TransmissionStart(Record):
    """TransmissionStart is the first record in every OCR file.

    A file can only contain a single transmission.

    Each transmission can contain any number of assignments.
    """

    transmission_number = attr.ib(validator=str_of_length(7))
    data_transmitter = attr.ib(validator=str_of_length(8))
    data_recipient = attr.ib(validator=str_of_length(8))

    RECORD_TYPE = netsgiro.RecordType.TRANSMISSION_START
    _PATTERNS = [
        re.compile(
            r'''
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
            ''',
            re.VERBOSE,
        )
    ]

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        return (
            'NY000010'
            f'{self.data_transmitter:8}'
            f'{self.transmission_number:7}'
            f'{self.data_recipient:8}'
            + ('0' * 49)
        )


@attr.s
class TransmissionEnd(Record):
    """TransmissionEnd is the first record in every OCR file."""

    num_transactions = attr.ib(converter=int)
    num_records = attr.ib(converter=int)
    total_amount = attr.ib(converter=int)
    nets_date = attr.ib(converter=to_date)

    RECORD_TYPE = netsgiro.RecordType.TRANSMISSION_END
    _PATTERNS = [
        re.compile(
            r'''
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
            ''',
            re.VERBOSE,
        )
    ]

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        return (
            'NY000089'
            f'{self.num_transactions:08d}'
            f'{self.num_records:08d}'
            f'{self.total_amount:017d}'
            f'{self.nets_date:%d%m%y}'
            + ('0' * 33)
        )


@attr.s
class AssignmentStart(Record):
    """AssignmentStart is the first record of an assignment.

    Each assignment can contain any number of transactions.
    """

    assignment_type = attr.ib(converter=to_assignment_type)
    assignment_number = attr.ib(validator=str_of_length(7))
    assignment_account = attr.ib(validator=str_of_length(11))

    # Only for assignment_type == AssignmentType.TRANSACTIONS
    agreement_id = attr.ib(default=None, validator=optional(str_of_length(9)))

    RECORD_TYPE = netsgiro.RecordType.ASSIGNMENT_START
    _PATTERNS = [
        re.compile(
            r'''
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
            ''',
            re.VERBOSE,
        ),
        re.compile(
            r'''
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
            ''',
            re.VERBOSE,
        ),
        re.compile(
            r'''
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
            ''',
            re.VERBOSE,
        ),
    ]

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        return (
            f'NY{self.service_code:02d}{self.assignment_type:02d}20'
            + (self.agreement_id and f'{self.agreement_id:9}' or ('0' * 9))
            + f'{self.assignment_number:7}{self.assignment_account:11}'
            + ('0' * 45)
        )


@attr.s
class AssignmentEnd(Record):
    """AssignmentEnd is the last record of an assignment."""

    assignment_type = attr.ib(converter=to_assignment_type)
    num_transactions = attr.ib(converter=int)
    num_records = attr.ib(converter=int)

    # Only for transactions and cancellations
    total_amount = attr.ib(default=None, converter=value_or_none(int))
    nets_date_1 = attr.ib(default=None, converter=to_date)
    nets_date_2 = attr.ib(default=None, converter=to_date)
    nets_date_3 = attr.ib(default=None, converter=to_date)

    RECORD_TYPE = netsgiro.RecordType.ASSIGNMENT_END
    _PATTERNS = [
        re.compile(
            r'''
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
            ''',
            re.VERBOSE,
        ),
        re.compile(
            r'''
            ^
            NY      # Format code
            (?P<service_code>21)
            (?P<assignment_type>24)     # AvtaleGiro agreements
            88      # Record type

            (?P<num_transactions>\d{8})
            (?P<num_records>\d{8})

            0{56}   # Filler
            $
            ''',
            re.VERBOSE,
        ),
        re.compile(
            r'''
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
            ''',
            re.VERBOSE,
        ),
    ]

    @property
    def nets_date(self):
        """Nets' processing date.

        Only used for OCR Giro.
        """
        if self.service_code == netsgiro.ServiceCode.OCR_GIRO:
            return self.nets_date_1
        else:
            return None

    @property
    def nets_date_earliest(self):
        """Earliest date from the contained transactions."""

        if self.service_code == netsgiro.ServiceCode.OCR_GIRO:
            return self.nets_date_2
        elif self.service_code == netsgiro.ServiceCode.AVTALEGIRO:
            return self.nets_date_1
        else:
            raise ValueError(f'Unhandled service code: {self.service_code}')

    @property
    def nets_date_latest(self):
        """Latest date from the contained transactions."""

        if self.service_code == netsgiro.ServiceCode.OCR_GIRO:
            return self.nets_date_3
        elif self.service_code == netsgiro.ServiceCode.AVTALEGIRO:
            return self.nets_date_2
        else:
            raise ValueError(f'Unhandled service code: {self.service_code}')

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        return (
            'NY'
            f'{self.service_code:02d}'
            f'{self.assignment_type:02d}'
            '88'
            f'{self.num_transactions:08d}'
            f'{self.num_records:08d}'
            + (self.total_amount and f'{self.total_amount:017d}' or ('0' * 17))
            + (self.nets_date_1 and f'{self.nets_date_1:%d%m%y}' or ('0' * 6))
            + (self.nets_date_2 and f'{self.nets_date_2:%d%m%y}' or ('0' * 6))
            + (self.nets_date_3 and f'{self.nets_date_3:%d%m%y}' or ('0' * 6))
            + ('0' * 21)
        )


@attr.s
class TransactionRecord(Record):
    transaction_type = attr.ib(converter=to_transaction_type)
    transaction_number = attr.ib(converter=int)


@attr.s
class TransactionAmountItem1(TransactionRecord):
    """TransactionAmountItem1 is the first record of a transaction.

    The record is used both for AvtaleGiro and for OCR Giro.
    """

    nets_date = attr.ib(converter=to_date)
    amount = attr.ib(converter=int)
    kid = attr.ib(
        converter=to_safe_str_or_none, validator=optional(str_of_max_length(25))
    )

    # Only OCR Giro
    centre_id = attr.ib(default=None, validator=optional(str_of_length(2)))
    day_code = attr.ib(default=None, converter=value_or_none(int))
    partial_settlement_number = attr.ib(
        default=None, converter=value_or_none(int)
    )
    partial_settlement_serial_number = attr.ib(
        default=None, validator=optional(str_of_length(5))
    )
    sign = attr.ib(default=None, validator=optional(str_of_length(1)))

    RECORD_TYPE = netsgiro.RecordType.TRANSACTION_AMOUNT_ITEM_1
    _PATTERNS = [
        re.compile(
            r'''
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
            ''',
            re.VERBOSE,
        ),
        re.compile(
            r'''
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
            ''',
            re.VERBOSE,
        ),
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
            f'{self.service_code:02d}'
            f'{self.transaction_type:02d}'
            '30'
            f'{self.transaction_number:07d}'
            f'{self.nets_date:%d%m%y}'
            + ocr_giro_fields
            + f'{self.amount:017d}{self.kid:>25}'
            + ('0' * 6)
        )


@attr.s
class TransactionAmountItem2(TransactionRecord):
    """TransactionAmountItem2 is the second record of a transaction.

    The record is used both for AvtaleGiro and for OCR Giro.
    """

    # TODO Validate `reference` length, which depends on service code
    reference = attr.ib(converter=to_safe_str_or_none)

    # Only OCR Giro
    form_number = attr.ib(default=None, validator=optional(str_of_length(10)))
    bank_date = attr.ib(default=None, converter=to_date)
    debit_account = attr.ib(default=None, validator=optional(str_of_length(11)))
    # XXX In use in OCR Giro "from giro debited account" transactions in test
    # data, but documented as a filler field.
    _filler = attr.ib(default=None)

    # Only AvtaleGiro
    payer_name = attr.ib(default=None, converter=to_safe_str_or_none)

    RECORD_TYPE = netsgiro.RecordType.TRANSACTION_AMOUNT_ITEM_2
    _PATTERNS = [
        re.compile(
            r'''
            ^
            NY      # Format code
            (?P<service_code>09)
            (?P<transaction_type>\d{2})  # 10-21
            31      # Record type

            (?P<transaction_number>\d{7})
            (?P<form_number>\d{10})
            (?P<reference>\d{9})

            (?P<filler>.{7})  # XXX Documented as filler, in use in test data

            (?P<bank_date>\d{6})
            (?P<debit_account>\d{11})

            0{22}    # Filler
            $
            ''',
            re.VERBOSE,
        ),
        re.compile(
            r'''
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
            ''',
            re.VERBOSE,
        ),
    ]

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        common_fields = (
            'NY'
            f'{self.service_code:02d}'
            f'{self.transaction_type:02d}'
            '31'
            f'{self.transaction_number:07d}'
        )
        if self.service_code == netsgiro.ServiceCode.OCR_GIRO:
            service_fields = (
                f'{self.form_number:10}'
                + (self.reference and f'{self.reference:9}' or (' ' * 9))
                + (self._filler and f'{self._filler:7}' or ('0' * 7))
                + (self.bank_date and f'{self.bank_date:%d%m%y}' or '0' * 6)
                + f'{self.debit_account:11}'
                + ('0' * 22)
            )
        elif self.service_code == netsgiro.ServiceCode.AVTALEGIRO:
            service_fields = (
                (self.payer_name and f'{self.payer_name[:10]:10}' or (' ' * 10))
                + (' ' * 25)
                + (self.reference and f'{self.reference:25}' or (' ' * 25))
                + ('0' * 5)
            )
        else:
            service_fields = ' ' * 35

        return common_fields + service_fields


@attr.s
class TransactionAmountItem3(TransactionRecord):
    """TransactionAmountItem3 is the third record of a transaction.

    The record is only used for some OCR Giro transaction types.
    """

    text = attr.ib(
        converter=to_safe_str_or_none, validator=optional(str_of_max_length(40))
    )

    RECORD_TYPE = netsgiro.RecordType.TRANSACTION_AMOUNT_ITEM_3
    _PATTERNS = [
        re.compile(
            r'''
            ^
            NY      # Format code
            (?P<service_code>09)
            (?P<transaction_type>\d{2})  # 20-21
            32      # Record type

            (?P<transaction_number>\d{7})
            (?P<text>.{40})

            0{25}    # Filler
            $
            ''',
            re.VERBOSE,
        )
    ]

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        return (
            f'NY09{self.transaction_type:02d}32{self.transaction_number:07d}'
            + (self.text and f'{self.text:40}' or (' ' * 40))
            + ('0' * 25)
        )


@attr.s
class TransactionSpecification(TransactionRecord):
    """TransactionSpecification is used for AvtaleGiro transactions.

    The record is only used when bank notification is used to notify the payer.

    Each record contains half of an 80 char long line of text and can be
    repeated up to 84 times for a single transaction for a total of 42 lines of
    specification text.
    """

    line_number = attr.ib(converter=int)
    column_number = attr.ib(converter=int)
    text = attr.ib(
        converter=stripped_newlines(fixed_len_str(40, str)),
        validator=optional(str_of_max_length(40)),
    )

    RECORD_TYPE = netsgiro.RecordType.TRANSACTION_SPECIFICATION
    _PATTERNS = [
        re.compile(
            r'''
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
            ''',
            re.VERBOSE,
        )
    ]

    _MAX_LINES = 42
    _MAX_LINE_LENGTH = 80
    _MAX_COLUMNS = 2
    _MAX_RECORDS = _MAX_LINES * _MAX_COLUMNS

    @classmethod
    def from_text(
        cls, *, service_code, transaction_type, transaction_number, text
    ) -> Iterable['TransactionSpecification']:
        """Create a sequence of specification records from a text string."""

        for line, column, text in cls._split_text_to_lines_and_columns(text):
            yield cls(
                service_code=service_code,
                transaction_type=transaction_type,
                transaction_number=transaction_number,
                line_number=line,
                column_number=column,
                text=text,
            )

    @classmethod
    def _split_text_to_lines_and_columns(
        cls, text
    ) -> Iterable[Tuple[int, int, str]]:
        lines = text.splitlines()

        if len(lines) > cls._MAX_LINES:
            raise ValueError(
                f'Max {cls._MAX_LINES} specification lines allowed, got {len(lines)}'
            )


        for line_number, line_text in enumerate(lines, 1):
            if len(line_text) > cls._MAX_LINE_LENGTH:
                raise ValueError(
                    'Specification lines must be max {} chars long, '
                    'got {}: {!r}'.format(
                        cls._MAX_LINE_LENGTH, len(line_text), line_text
                    )
                )

            yield (line_number, 1, f'{line_text[:40]:40}')
            yield (line_number, 2, f'{line_text[40:80]:40}')

    @classmethod
    def to_text(cls, records: Sequence['TransactionSpecification']) -> str:
        """Get a text string from a sequence of specification records."""

        if len(records) > cls._MAX_RECORDS:
            raise ValueError(
                f'Max {cls._MAX_RECORDS} specification records allowed, got {len(records)}'
            )


        tuples = sorted((r.line_number, r.column_number, r) for r in records)

        text = ''
        for _, column, specification in tuples:
            text += specification.text
            if column == cls._MAX_COLUMNS:
                text += '\n'

        return text

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        return (
            'NY212149'
            f'{self.transaction_number:07d}'
            '4'
            f'{self.line_number:03d}'
            f'{self.column_number:01d}'
            f'{self.text:40}'
            + ('0' * 20)
        )


@attr.s
class AvtaleGiroAgreement(TransactionRecord):
    """AvtaleGiroAgreement is used by Nets to notify about agreement changes.

    This includes new or deleted agreements, as well as updates to the payer's
    notification preferences.
    """

    registration_type = attr.ib(converter=to_avtalegiro_registration_type)
    kid = attr.ib(
        converter=to_safe_str_or_none, validator=optional(str_of_max_length(25))
    )
    notify = attr.ib(converter=to_bool)

    RECORD_TYPE = netsgiro.RecordType.TRANSACTION_AGREEMENTS
    _PATTERNS = [
        re.compile(
            r'''
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
            ''',
            re.VERBOSE,
        )
    ]

    def to_ocr(self) -> str:
        """Get record as OCR string."""
        return (
            'NY219470'
            f'{self.transaction_number:07d}'
            f'{self.registration_type:01d}'
            f'{self.kid:>25}'
            + (self.notify and 'J' or 'N')
            + ('0' * 38)
        ).format(self=self)


def parse(data: str) -> List[Record]:
    """Parse an OCR file into a list of record objects."""

    def all_subclasses(cls):
        return cls.__subclasses__() + [
            subsubcls
            for subcls in cls.__subclasses__()
            for subsubcls in all_subclasses(subcls)
        ]

    record_classes = {
        cls.RECORD_TYPE: cls
        for cls in all_subclasses(Record)
        if hasattr(cls, 'RECORD_TYPE')
    }

    results = []

    for line in data.strip().splitlines():
        if len(line) != 80:
            raise ValueError('All lines must be exactly 80 chars long')

        record_type_str = line[6:8]
        if not record_type_str.isnumeric():
            raise ValueError(
                f'Record type must be numeric, got {record_type_str!r}'
            )

        record_type = netsgiro.RecordType(int(record_type_str))
        record_cls = record_classes[record_type]

        results.append(record_cls.from_string(line))

    return results
