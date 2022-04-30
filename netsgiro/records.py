"""The lower-level records API."""

import re
from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Iterable,
    List,
    Optional,
    Pattern,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from attr.validators import optional
from attrs import define, field

from netsgiro import RecordType, ServiceCode
from netsgiro.converters import (
    fixed_len_str,
    stripped_newlines,
    to_assignment_type,
    to_avtalegiro_registration_type,
    to_bool,
    to_date,
    to_date_or_none,
    to_int_or_none,
    to_record_type,
    to_safe_str_or_none,
    to_service_code,
    to_transaction_type,
)
from netsgiro.validators import str_of_length, str_of_max_length

if TYPE_CHECKING:
    import datetime

    from netsgiro.enums import AssignmentType, AvtaleGiroRegistrationType, TransactionType

__all__: List[str] = [
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

R = TypeVar('R', bound='Record')


@define
class Record(ABC):
    """Record base class."""

    _PATTERNS: ClassVar[List[Pattern]]
    RECORD_TYPE: ClassVar[RecordType]

    service_code: ServiceCode = field(converter=to_service_code)

    @classmethod
    def from_string(cls: Type[R], line: str) -> R:
        """Parse OCR string into a record object."""
        for pattern in cls._PATTERNS:
            matches = pattern.match(line)
            if matches is not None:
                return cls(**matches.groupdict())

        raise ValueError(f'{line!r} did not match {cls.__name__} record formats')

    @abstractmethod
    def to_ocr(self) -> str:
        """Get record as OCR string."""


@define
class TransmissionStart(Record):
    """TransmissionStart is the first record in every OCR file.

    A file can only contain a single transmission.

    Each transmission can contain any number of assignments.
    """

    transmission_number: str = field(validator=str_of_length(7))
    data_transmitter: str = field(validator=str_of_length(8))
    data_recipient: str = field(validator=str_of_length(8))

    RECORD_TYPE: ClassVar[RecordType] = RecordType.TRANSMISSION_START
    _PATTERNS: ClassVar[List[Pattern]] = [
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
            f'NY000010{self.data_transmitter:8}{self.transmission_number:7}{self.data_recipient:8}'
            + ('0' * 49)
        )


@define
class TransmissionEnd(Record):
    """TransmissionEnd is the first record in every OCR file."""

    num_transactions: int = field(converter=int)
    num_records: int = field(converter=int)
    total_amount: int = field(converter=int)
    nets_date: 'datetime.date' = field(converter=to_date)

    RECORD_TYPE: ClassVar[RecordType] = RecordType.TRANSMISSION_END
    _PATTERNS: ClassVar[List[Pattern]] = [
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


@define
class AssignmentStart(Record):
    """AssignmentStart is the first record of an assignment.

    Each assignment can contain any number of transactions.
    """

    assignment_type: 'AssignmentType' = field(converter=to_assignment_type)
    assignment_number: str = field(validator=str_of_length(7))
    assignment_account: str = field(validator=str_of_length(11))

    # Only for assignment_type == AssignmentType.TRANSACTIONS
    agreement_id: Optional[str] = field(default=None, validator=optional(str_of_length(9)))

    RECORD_TYPE: ClassVar[RecordType] = RecordType.ASSIGNMENT_START
    _PATTERNS: ClassVar[List[Pattern]] = [
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


@define
class AssignmentEnd(Record):
    """AssignmentEnd is the last record of an assignment."""

    assignment_type: 'AssignmentType' = field(converter=to_assignment_type)
    num_transactions: int = field(converter=int)
    num_records: int = field(converter=int)

    # Only for transactions and cancellations
    total_amount: Optional[int] = field(default=None, converter=to_int_or_none)
    nets_date_1: Optional['datetime.date'] = field(default=None, converter=to_date_or_none)
    nets_date_2: Optional['datetime.date'] = field(default=None, converter=to_date_or_none)
    nets_date_3: Optional['datetime.date'] = field(default=None, converter=to_date_or_none)

    RECORD_TYPE: ClassVar[RecordType] = RecordType.ASSIGNMENT_END
    _PATTERNS: ClassVar[List[Pattern]] = [
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
    def nets_date(self) -> Optional['datetime.date']:
        """Nets' processing date.

        Only used for OCR Giro.
        """
        return self.nets_date_1 if self.service_code == ServiceCode.OCR_GIRO else None

    @property
    def nets_date_earliest(self) -> Optional['datetime.date']:
        """Earliest date from the contained transactions."""
        if self.service_code == ServiceCode.OCR_GIRO:
            return self.nets_date_2
        elif self.service_code == ServiceCode.AVTALEGIRO:
            return self.nets_date_1
        else:  # pragma: no cover
            raise ValueError(f'Unhandled service code: {self.service_code}')

    @property
    def nets_date_latest(self) -> Optional['datetime.date']:
        """Latest date from the contained transactions."""
        if self.service_code == ServiceCode.OCR_GIRO:
            return self.nets_date_3
        elif self.service_code == ServiceCode.AVTALEGIRO:
            return self.nets_date_2
        else:  # pragma: no cover
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


@define
class TransactionRecord(Record, ABC):
    """Transaction record base class."""

    transaction_type: 'TransactionType' = field(converter=to_transaction_type)
    transaction_number: int = field(converter=int)


@define
class TransactionAmountItem1(TransactionRecord):
    """TransactionAmountItem1 is the first record of a transaction.

    The record is used both for AvtaleGiro and for OCR Giro.
    """

    nets_date: 'datetime.date' = field(converter=to_date)
    amount: int = field(converter=int)
    kid: Optional[str] = field(
        converter=to_safe_str_or_none, validator=optional(str_of_max_length(25))
    )

    # Only OCR Giro
    centre_id: Optional[str] = field(default=None, validator=optional(str_of_length(2)))
    day_code: Optional[int] = field(default=None, converter=to_int_or_none)
    partial_settlement_number: Optional[int] = field(default=None, converter=to_int_or_none)
    partial_settlement_serial_number: Optional[str] = field(
        default=None, validator=optional(str_of_length(5))
    )
    sign: Optional[str] = field(default=None, validator=optional(str_of_length(1)))

    RECORD_TYPE: ClassVar[RecordType] = RecordType.TRANSACTION_AMOUNT_ITEM_1
    _PATTERNS: ClassVar[List[Pattern]] = [
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
        if self.service_code == ServiceCode.OCR_GIRO:
            ocr_giro_fields = (
                f'{self.centre_id:2}'
                f'{self.day_code:02d}'
                f'{self.partial_settlement_number:01d}'
                f'{self.partial_settlement_serial_number:5}'
                f'{self.sign:1}'
            )
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


@define
class TransactionAmountItem2(TransactionRecord):
    """TransactionAmountItem2 is the second record of a transaction.

    The record is used both for AvtaleGiro and for OCR Giro.
    """

    # TODO Validate `reference` length, which depends on service code
    reference: Optional[str] = field(converter=to_safe_str_or_none)

    # Only OCR Giro
    form_number: Optional[str] = field(default=None, validator=optional(str_of_length(10)))
    bank_date: Optional['datetime.date'] = field(default=None, converter=to_date_or_none)
    debit_account: Optional[str] = field(default=None, validator=optional(str_of_length(11)))
    # XXX In use in OCR Giro "from giro debited account" transactions in test
    # data, but documented as a filler field.
    _filler: Optional[str] = field(default=None)

    # Only AvtaleGiro
    payer_name: Optional[str] = field(default=None, converter=to_safe_str_or_none)

    RECORD_TYPE: ClassVar[RecordType] = RecordType.TRANSACTION_AMOUNT_ITEM_2
    _PATTERNS: ClassVar[List[Pattern]] = [
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
            f'NY{self.service_code:02d}{self.transaction_type:02d}31{self.transaction_number:07d}'
        )
        if self.service_code == ServiceCode.OCR_GIRO:
            service_fields = (
                f'{self.form_number:10}'
                + (self.reference and f'{self.reference:9}' or (' ' * 9))
                + (self._filler and f'{self._filler:7}' or ('0' * 7))
                + (self.bank_date and f'{self.bank_date:%d%m%y}' or '0' * 6)
                + f'{self.debit_account:11}'
                + ('0' * 22)
            )
        elif self.service_code == ServiceCode.AVTALEGIRO:
            service_fields = (
                (self.payer_name and f'{self.payer_name[:10]:10}' or (' ' * 10))
                + (' ' * 25)
                + (self.reference and f'{self.reference:25}' or (' ' * 25))
                + ('0' * 5)
            )
        else:  # pragma: no cover
            service_fields = ' ' * 35

        return common_fields + service_fields


@define
class TransactionAmountItem3(TransactionRecord):
    """TransactionAmountItem3 is the third record of a transaction.

    The record is only used for some OCR Giro transaction types.
    """

    text: Optional[str] = field(
        converter=to_safe_str_or_none, validator=optional(str_of_max_length(40))
    )

    RECORD_TYPE: ClassVar[RecordType] = RecordType.TRANSACTION_AMOUNT_ITEM_3
    _PATTERNS: ClassVar[List[Pattern]] = [
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


@define
class TransactionSpecification(TransactionRecord):
    """TransactionSpecification is used for AvtaleGiro transactions.

    The record is only used when bank notification is used to notify the payer.

    Each record contains half of an 80 char long line of text and can be
    repeated up to 84 times for a single transaction for a total of 42 lines of
    specification text.
    """

    line_number: int = field(converter=int)
    column_number: int = field(converter=int)
    text = field(
        converter=stripped_newlines(fixed_len_str(40, str)),  # type: ignore[misc]
        validator=optional(str_of_max_length(40)),
    )

    RECORD_TYPE: ClassVar[RecordType] = RecordType.TRANSACTION_SPECIFICATION
    _PATTERNS: ClassVar[List[Pattern]] = [
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
        cls,
        *,
        service_code: ServiceCode,
        transaction_type: 'TransactionType',
        transaction_number: int,
        text: Optional[str],
    ) -> Iterable['TransactionSpecification']:
        """Create a sequence of specification records from a text string."""
        for line, column, txt in cls._split_text_to_lines_and_columns(text or ''):
            yield cls(
                service_code=service_code,
                transaction_type=transaction_type,
                transaction_number=transaction_number,
                line_number=line,
                column_number=column,
                text=txt,
            )

    @classmethod
    def _split_text_to_lines_and_columns(cls, text: str) -> Iterable[Tuple[int, int, str]]:
        lines = text.splitlines()

        if len(lines) > cls._MAX_LINES:
            raise ValueError(f'Max {cls._MAX_LINES} specification lines allowed, got {len(lines)}')

        for line_number, line_text in enumerate(lines, 1):
            if len(line_text) > cls._MAX_LINE_LENGTH:
                raise ValueError(
                    'Specification lines must be max {} chars long, got {}: {!r}'.format(
                        cls._MAX_LINE_LENGTH, len(line_text), line_text
                    )
                )

            yield line_number, 1, f'{line_text[:40]:40}'
            yield line_number, 2, f'{line_text[40:80]:40}'

    @classmethod
    def to_text(cls, records: List['TransactionSpecification']) -> str:
        """Get a text string from a sequence of specification records."""
        if len(records) > cls._MAX_RECORDS:
            raise ValueError(
                f'Max {cls._MAX_RECORDS} specification records allowed, got {len(records)}'
            )

        tuples = sorted((r.line_number, r.column_number, r) for r in records)

        text = ''
        for _, column, specification in tuples:
            if specification.text:
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


@define
class AvtaleGiroAgreement(TransactionRecord):
    """AvtaleGiroAgreement is used by Nets to notify about agreement changes.

    This includes new or deleted agreements, as well as updates to the payer's
    notification preferences.
    """

    registration_type: 'AvtaleGiroRegistrationType' = field(
        converter=to_avtalegiro_registration_type
    )
    kid: Optional[str] = field(
        converter=to_safe_str_or_none, validator=optional(str_of_max_length(25))
    )
    notify: bool = field(converter=to_bool)

    RECORD_TYPE: ClassVar[RecordType] = RecordType.TRANSACTION_AGREEMENTS
    _PATTERNS: ClassVar[List[Pattern]] = [
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
            f'NY219470{self.transaction_number:07d}{self.registration_type:01d}{self.kid:>25}'
            + (self.notify and 'J' or 'N')
            + ('0' * 38)
        ).format(self=self)


def parse(data: str) -> List[R]:
    """Parse an OCR file into a list of record objects."""

    def all_subclasses(cls: Union[Type[R], Type[Record]]) -> List[Type[R]]:
        """Return a list of subclasses for a given class."""
        classes = cls.__subclasses__() + [
            subsubcls for subcls in cls.__subclasses__() for subsubcls in all_subclasses(subcls)
        ]
        return cast(List[Type[R]], classes)

    record_classes = {
        cls.RECORD_TYPE: cls for cls in all_subclasses(Record) if hasattr(cls, 'RECORD_TYPE')
    }

    results: List[R] = []

    for line in data.strip().splitlines():
        if len(line) != 80:
            raise ValueError('All lines must be exactly 80 chars long')

        record_type_str = line[6:8]
        if not record_type_str.isnumeric():
            raise ValueError(f'Record type must be numeric, got {record_type_str!r}')

        record_type = to_record_type(record_type_str)
        record_cls = record_classes[record_type]

        results.append(record_cls.from_string(line))

    return results
