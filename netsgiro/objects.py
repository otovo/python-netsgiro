"""The higher-level objects API."""

import datetime
from collections import OrderedDict
from decimal import Decimal
from typing import TYPE_CHECKING, Callable, ClassVar, Iterable, List, Optional
from typing import OrderedDict as OrderedDictType
from typing import TypeVar, Union, cast

from attrs import Factory, define, field
from attrs.validators import instance_of, optional

from netsgiro.converters import (
    to_assignment_type,
    to_avtalegiro_registration_type,
    to_service_code,
    to_transaction_type,
)
from netsgiro.enums import AssignmentType, ServiceCode, TransactionType
from netsgiro.records import (
    AssignmentEnd,
    AssignmentStart,
    AvtaleGiroAgreement,
    TransactionAmountItem1,
    TransactionAmountItem2,
    TransactionAmountItem3,
    TransactionRecord,
    TransactionSpecification,
    TransmissionEnd,
    TransmissionStart,
)
from netsgiro.records import parse as records_parse
from netsgiro.validators import str_of_length
from netsgiro.validators import validate_due_date as _validate_due_date

if TYPE_CHECKING:
    from netsgiro.enums import AvtaleGiroRegistrationType
    from netsgiro.records import Record

__all__: List[str] = [
    'Transmission',
    'Assignment',
    'Agreement',
    'PaymentRequest',
    'Transaction',
    'parse',
]

TransactionAmountItems = Union[
    TransactionAmountItem1, TransactionAmountItem2, TransactionAmountItem3
]

# Record or Record subclasses
R = TypeVar('R', bound='Record')


@define
class Transmission:
    """Transmission is the top-level object.

    An OCR file contains a single transmission. The transmission can contain
    multiple :class:`~netsgiro.Assignment` objects of various types.
    """

    #: Data transmitters unique enumeration of the transmission. String of 7 digits.
    number: str = field(validator=str_of_length(7))

    #: Data transmitter's Nets ID. String of 8 digits.
    data_transmitter: str = field(validator=str_of_length(8))

    #: Data recipient's Nets ID. String of 8 digits.
    data_recipient: str = field(validator=str_of_length(8))

    #: For OCR Giro files from Nets, this is Nets' processing date.
    #:
    #: For AvtaleGiro payment request, the earliest due date in the
    #: transmission is automatically used.
    date: Optional[datetime.date] = field(
        default=None, validator=optional(instance_of(datetime.date))
    )

    #: List of assignments.
    assignments: List['Assignment'] = field(default=Factory(list), repr=False)

    @classmethod
    def from_records(cls, records: List[R]) -> 'Transmission':
        """Build a Transmission object from a list of record objects."""
        if len(records) < 2:
            raise ValueError(f'At least 2 records required, got {len(records)}')

        start, body, end = records[0], records[1:-1], records[-1]

        assert isinstance(start, TransmissionStart)
        assert isinstance(end, TransmissionEnd)

        return cls(
            number=start.transmission_number,
            data_transmitter=start.data_transmitter,
            data_recipient=start.data_recipient,
            date=end.nets_date,
            assignments=cls._get_assignments(body),
        )

    @staticmethod
    def _get_assignments(records: List[R]) -> List['Assignment']:
        assignments: OrderedDictType[str, List[R]] = OrderedDict()

        current_assignment_number = None
        for record in records:
            if isinstance(record, AssignmentStart):
                current_assignment_number = record.assignment_number
                assignments[current_assignment_number] = []
            if current_assignment_number is None:
                raise ValueError(f'Expected AssignmentStart record, got {record!r}')
            assignments[current_assignment_number].append(record)
            if isinstance(record, AssignmentEnd):
                current_assignment_number = None

        return [Assignment.from_records(rs) for rs in assignments.values()]

    def to_ocr(self) -> str:
        """Convert the transmission to an OCR string."""
        lines = [record.to_ocr() for record in self.to_records()]
        return '\n'.join(lines)

    def to_records(self) -> Iterable['Record']:
        """Convert the transmission to a list of records."""
        yield self._get_start_record()
        for assignment in self.assignments:
            yield from assignment.to_records()
        yield self._get_end_record()

    def _get_start_record(self) -> 'Record':
        return TransmissionStart(
            service_code=ServiceCode.NONE,
            transmission_number=self.number,
            data_transmitter=self.data_transmitter,
            data_recipient=self.data_recipient,
        )

    def _get_end_record(self) -> 'Record':
        avtalegiro_payment_request = all(
            assignment.service_code == ServiceCode.AVTALEGIRO
            and assignment.type
            in (
                AssignmentType.TRANSACTIONS,
                AssignmentType.AVTALEGIRO_CANCELLATIONS,
            )
            for assignment in self.assignments
        )
        if self.assignments and avtalegiro_payment_request:
            date: Optional[datetime.date] = None
            for assignment in self.assignments:
                earliest_transaction_date = assignment.get_earliest_transaction_date()
                if date is None or (
                    isinstance(earliest_transaction_date, datetime.date)
                    and earliest_transaction_date < date
                ):
                    date = earliest_transaction_date
        else:
            date = self.date

        assert isinstance(date, datetime.date)

        return TransmissionEnd(
            service_code=ServiceCode.NONE,
            num_transactions=self.get_num_transactions(),
            num_records=self.get_num_records(),
            total_amount=int(self.get_total_amount() * 100),
            nets_date=date,
        )

    def add_assignment(
        self,
        *,
        service_code: ServiceCode,
        assignment_type: AssignmentType,
        agreement_id: Optional[str] = None,
        number: str,
        account: str,
        date: Optional[datetime.date] = None,
    ) -> 'Assignment':
        """Add an assignment to the transmission."""
        assignment = Assignment(
            service_code=service_code,
            type=assignment_type,
            agreement_id=agreement_id,
            number=number,
            account=account,
            date=date,
        )
        self.assignments.append(assignment)
        return assignment

    def get_num_transactions(self) -> int:
        """Get number of transactions in the transmission."""
        return sum(assignment.get_num_transactions() for assignment in self.assignments)

    def get_num_records(self) -> int:
        """Get number of records in the transmission.

        Includes the transmission's start and end record.
        """
        return 2 + sum(assignment.get_num_records() for assignment in self.assignments)

    def get_total_amount(self) -> Decimal:
        """Get the total amount from all transactions in the transmission."""
        return Decimal(sum(assignment.get_total_amount() for assignment in self.assignments))


# Assigment transactions
TS = List[Union['Transaction', 'Agreement', 'PaymentRequest']]

# TransactionRecord and subclasses
TR = TypeVar('TR', bound=TransactionRecord)


@define
class Assignment:
    """An Assignment groups multiple transactions within a transmission.

    Use :meth:`netsgiro.Transmission.add_assignment` to create assignments.
    """

    #: The service code. One of :class:`~netsgiro.ServiceCode`.
    service_code: ServiceCode = field(converter=to_service_code)

    #: The transaction type. One of :class:`~TransactionType`.
    type: AssignmentType = field(converter=to_assignment_type)

    #: The assignment number. String of 7 digits.
    number: str = field(validator=str_of_length(7))

    #: The payee's bank account. String of 11 digits.
    account: str = field(validator=str_of_length(11))

    #: Used for OCR Giro.
    #:
    #: The payee's agreement ID with Nets. String of 9 digits.
    agreement_id: Optional[str] = field(default=None, validator=optional(str_of_length(9)))

    #: Used for OCR Giro.
    #:
    #: The date the assignment was generated by Nets.
    date: Optional[datetime.date] = field(
        default=None, validator=optional(instance_of(datetime.date))
    )

    #: List of transaction objects, like :class:`~netsgiro.Agreement`,
    #: :class:`~netsgiro.PaymentRequest`, :class:`~netsgiro.Transaction`.
    transactions: TS = field(default=Factory(list), repr=False)

    _next_transaction_number: int = field(default=1, init=False)

    @classmethod
    def from_records(cls, records: List[R]) -> 'Assignment':
        """Build an Assignment object from a list of record objects."""
        if len(records) < 2:
            raise ValueError(f'At least 2 records required, got {len(records)}')

        start, body, end = records[0], records[1:-1], records[-1]

        assert isinstance(start, AssignmentStart)
        assert isinstance(end, AssignmentEnd)

        sc = start.service_code
        at = start.assignment_type

        cb: Callable
        if sc == ServiceCode.OCR_GIRO:
            # -> List[Transaction]
            cb = cls._get_transactions
        elif sc == ServiceCode.AVTALEGIRO:
            if at == AssignmentType.AVTALEGIRO_AGREEMENTS:
                # -> List[Agreement]
                cb = cls._get_agreements
            else:
                # -> List[PaymentRequest]
                cb = cls._get_payment_requests
        else:  # pragma: no cover
            raise ValueError(f'Unknown service code: {start.service_code}')

        transactions: TS = cb(body)

        return cls(
            service_code=start.service_code,
            type=start.assignment_type,
            agreement_id=start.agreement_id,
            number=start.assignment_number,
            account=start.assignment_account,
            date=end.nets_date,
            transactions=transactions,
        )

    @staticmethod
    def _get_agreements(records: List[AvtaleGiroAgreement]) -> List['Agreement']:
        return [Agreement.from_records([r]) for r in records]

    @classmethod
    def _get_payment_requests(cls, records: List[TR]) -> List['PaymentRequest']:
        transactions = cls._group_by_transaction_number(records)
        return [PaymentRequest.from_records(rs) for rs in transactions.values()]

    @classmethod
    def _get_transactions(cls, records: List[TR]) -> List['Transaction']:
        transactions = cls._group_by_transaction_number(records)
        return [Transaction.from_records(rs) for rs in transactions.values()]

    @staticmethod
    def _group_by_transaction_number(records: List[TR]) -> OrderedDictType[int, List[TR]]:
        transactions: OrderedDictType[int, List[TR]] = OrderedDict()
        for transaction_record in records:
            tr = transaction_record.transaction_number
            if tr not in transactions:
                transactions[tr] = []
            transactions[tr].append(transaction_record)

        return transactions

    def to_records(self) -> Iterable[Union[AssignmentStart, TransactionAmountItems, AssignmentEnd]]:
        """Convert the assignment to a list of records."""
        yield self._get_start_record()
        for transaction in self.transactions:
            yield from transaction.to_records()
        yield self._get_end_record()

    def _get_start_record(self) -> AssignmentStart:
        return AssignmentStart(
            service_code=self.service_code,
            assignment_type=self.type,
            assignment_number=self.number,
            assignment_account=self.account,
            agreement_id=self.agreement_id,
        )

    def _get_end_record(self) -> AssignmentEnd:
        if self.service_code == ServiceCode.OCR_GIRO:
            dates = {
                'nets_date_1': self.date,
                'nets_date_2': self.get_earliest_transaction_date(),
                'nets_date_3': self.get_latest_transaction_date(),
            }
        elif self.service_code == ServiceCode.AVTALEGIRO:
            dates = {
                'nets_date_1': self.get_earliest_transaction_date(),
                'nets_date_2': self.get_latest_transaction_date(),
            }
        else:  # pragma: no cover
            raise ValueError(f'Unhandled service code: {self.service_code}')

        return AssignmentEnd(
            service_code=self.service_code,
            assignment_type=self.type,
            num_transactions=self.get_num_transactions(),
            num_records=self.get_num_records(),
            total_amount=int(self.get_total_amount() * 100),
            **dates,
        )

    def add_payment_request(
        self,
        *,
        kid: str,
        due_date: datetime.date,
        amount: Decimal,
        reference: Optional[str] = None,
        payer_name: Optional[str] = None,
        bank_notification: Union[bool, str] = False,
        validate_due_date: bool = False,
    ) -> 'PaymentRequest':
        """Add an AvtaleGiro payment request to the assignment.

        The assignment must have service code
        :attr:`~ServiceCode.AVTALEGIRO` and assignment type
        :attr:`~AssignmentType.TRANSACTIONS`.
        """
        assert (
            self.service_code == ServiceCode.AVTALEGIRO
        ), 'Can only add payment requests to AvtaleGiro assignments'
        assert (
            self.type == AssignmentType.TRANSACTIONS
        ), 'Can only add payment requests to transaction assignments'

        if validate_due_date:
            # Make sure we're not passing invalid due dates
            _validate_due_date(due_date)

        if bank_notification:
            transaction_type = TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION
        else:
            transaction_type = TransactionType.AVTALEGIRO_WITH_PAYEE_NOTIFICATION

        return self._add_avtalegiro_transaction(
            transaction_type=transaction_type,
            kid=kid,
            due_date=due_date,
            amount=amount,
            reference=reference,
            payer_name=payer_name,
            bank_notification=bank_notification,
        )

    def add_payment_cancellation(
        self,
        *,
        kid: str,
        due_date: datetime.date,
        amount: Decimal,
        reference: Optional[str] = None,
        payer_name: Optional[str] = None,
        bank_notification: Union[bool, str] = False,
    ) -> 'PaymentRequest':
        """Add an AvtaleGiro cancellation to the assignment.

        The assignment must have service code
        :attr:`~netsgiro.ServiceCode.AVTALEGIRO` and assignment type
        :attr:`~AssignmentType.AVTALEGIRO_CANCELLATIONS`.

        Otherwise, the cancellation must be identical to the payment request it
        is cancelling.
        """
        assert (
            self.service_code == ServiceCode.AVTALEGIRO
        ), 'Can only add cancellation to AvtaleGiro assignments'
        assert (
            self.type == AssignmentType.AVTALEGIRO_CANCELLATIONS
        ), 'Can only add cancellation to cancellation assignments'

        return self._add_avtalegiro_transaction(
            transaction_type=TransactionType.AVTALEGIRO_CANCELLATION,
            kid=kid,
            due_date=due_date,
            amount=amount,
            reference=reference,
            payer_name=payer_name,
            bank_notification=bank_notification,
        )

    def _add_avtalegiro_transaction(
        self,
        *,
        transaction_type: TransactionType,
        kid: str,
        due_date: datetime.date,
        amount: Decimal,
        reference: Optional[str] = None,
        payer_name: Optional[str] = None,
        bank_notification: Union[str, bool] = False,
    ) -> 'PaymentRequest':

        text = bank_notification if isinstance(bank_notification, str) else ''
        number = self._next_transaction_number
        self._next_transaction_number += 1

        transaction = PaymentRequest(
            service_code=self.service_code,
            type=transaction_type,
            number=number,
            date=due_date,
            amount=amount,
            kid=kid,
            reference=reference,
            text=text,
            payer_name=payer_name,
        )
        self.transactions.append(transaction)
        return transaction

    def get_num_transactions(self) -> int:
        """Get number of transactions in the assignment."""
        return len(self.transactions)

    def get_num_records(self) -> int:
        """Get number of records in the assignment.

        Includes the assignment's start and end record.
        """
        return 2 + sum(len(list(transaction.to_records())) for transaction in self.transactions)

    def get_total_amount(self) -> Decimal:
        """Get the total amount from all transactions in the assignment."""
        total = Decimal(0)
        for t in self.transactions:
            iter_amount = getattr(t, 'amount', None)
            if iter_amount:
                total += iter_amount
        return total

    def _get_earliest_or_latest_transaction_date(self, latest: bool) -> Optional[datetime.date]:
        """Get earliest or latest date from the assignment's transactions."""
        date_: Optional[datetime.date] = None
        for t in self.transactions:
            iter_date = getattr(t, 'date', None)
            if iter_date and (
                date_ is None or (iter_date > date_ if latest else iter_date < date_)
            ):
                date_ = iter_date
        return date_

    def get_earliest_transaction_date(self) -> Optional[datetime.date]:
        """Get earliest date from the assignment's transactions."""
        return self._get_earliest_or_latest_transaction_date(latest=False)

    def get_latest_transaction_date(self) -> Optional[datetime.date]:
        """Get latest date from the assignment's transactions."""
        return self._get_earliest_or_latest_transaction_date(latest=True)


@define
class Agreement:
    """Agreement contains an AvtaleGiro agreement update.

    Agreements are only found in assignments of the
    :attr:`~AssignmentType.AVTALEGIRO_AGREEMENTS` type, which are only
    created by Nets.
    """

    #: The service code. One of :class:`~netsgiro.ServiceCode`.
    service_code: ServiceCode = field(converter=to_service_code)

    #: Transaction number. Unique and ordered within an assignment.
    number: int = field(validator=instance_of(int))

    #: Type of agreement registration update.
    #: One of :class:`~AvtaleGiroRegistrationType`.
    registration_type: 'AvtaleGiroRegistrationType' = field(
        converter=to_avtalegiro_registration_type
    )

    #: KID number to identify the customer and invoice.
    kid: Optional[str] = field(validator=optional(instance_of(str)))

    #: Whether the payer wants notification about payment requests.
    notify: bool = field(validator=instance_of(bool))

    TRANSACTION_TYPE: ClassVar[TransactionType] = TransactionType.AVTALEGIRO_AGREEMENT

    @classmethod
    def from_records(cls, records: List[AvtaleGiroAgreement]) -> 'Agreement':
        """Build an Agreement object from a list of record objects."""
        assert len(records) == 1
        record = records[0]
        assert isinstance(record, AvtaleGiroAgreement)
        assert record.transaction_type == TransactionType.AVTALEGIRO_AGREEMENT

        return cls(
            service_code=record.service_code,
            number=record.transaction_number,
            registration_type=record.registration_type,
            kid=record.kid,
            notify=record.notify,
        )

    def to_records(self) -> Iterable[AvtaleGiroAgreement]:
        """Convert the agreement to a list of records."""
        yield AvtaleGiroAgreement(
            service_code=self.service_code,
            transaction_type=self.TRANSACTION_TYPE,
            transaction_number=self.number,
            registration_type=self.registration_type,
            kid=self.kid,
            notify=self.notify,
        )


@define
class PaymentRequest:
    """PaymentRequest contains an AvtaleGiro payment request or cancellation.

    To create a transaction, you will normally use the helper methods on
    :class:`~netsgiro.Assignment`:
    :meth:`~netsgiro.Assignment.add_payment_request` and
    :meth:`~netsgiro.Assignment.add_payment_cancellation`.
    """

    #: The service code. One of :class:`~netsgiro.ServiceCode`.
    service_code: ServiceCode = field(converter=to_service_code)

    #: The transaction type. One of :class:`~TransactionType`.
    type: TransactionType = field(converter=to_transaction_type)

    #: Transaction number. Unique and ordered within an assignment.
    number: int = field(validator=instance_of(int))

    #: The due date.
    date: datetime.date = field(validator=instance_of(datetime.date))

    #: Transaction amount in NOK with two decimals.
    amount: Decimal = field(converter=Decimal)

    #: KID number to identify the customer and invoice.
    kid: Optional[str] = field(validator=optional(instance_of(str)))

    #: This is a specification line that will, if set, be displayed on the
    #: payers account statement. Alphanumeric, max 25 chars.
    reference: Optional[str] = field(validator=optional(instance_of(str)))

    #: This is up to 42 lines of 80 chars each of free text used by the bank to
    #: notify the payer about the payment request. It is not used if the payee
    #: is responsible for notifying the payer.
    text: Optional[str] = field(validator=optional(instance_of(str)))

    #: The value is only used to help the payee cross-reference reports from
    #: Nets with their own records. It is not vi.attr.ible to the payer.
    payer_name: Optional[str] = field(validator=optional(instance_of(str)))

    @property
    def amount_in_cents(self) -> int:
        """Transaction amount in NOK cents."""
        return int(self.amount * 100)

    @classmethod
    def from_records(cls, records: List[TR]) -> 'PaymentRequest':
        """Build a Transaction object from a list of record objects."""
        amount_item_1 = records.pop(0)
        assert isinstance(amount_item_1, TransactionAmountItem1)
        amount_item_2 = records.pop(0)
        assert isinstance(amount_item_2, TransactionAmountItem2)

        text = TransactionSpecification.to_text(cast(List['TransactionSpecification'], records))

        return cls(
            service_code=amount_item_1.service_code,
            type=amount_item_1.transaction_type,
            number=amount_item_1.transaction_number,
            date=amount_item_1.nets_date,
            amount=Decimal(amount_item_1.amount) / 100,
            kid=amount_item_1.kid,
            reference=amount_item_2.reference,
            text=text,
            payer_name=amount_item_2.payer_name,
        )

    def to_records(
        self,
    ) -> Iterable[Union[TransactionAmountItem1, TransactionAmountItem2, TransactionSpecification]]:
        """Convert the transaction to a list of records."""
        yield TransactionAmountItem1(
            service_code=self.service_code,
            transaction_type=self.type,
            transaction_number=self.number,
            nets_date=self.date,
            amount=self.amount_in_cents,
            kid=self.kid,
        )
        yield TransactionAmountItem2(
            service_code=self.service_code,
            transaction_type=self.type,
            transaction_number=self.number,
            reference=self.reference,
            payer_name=self.payer_name,
        )

        if self.type == TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION:
            yield from TransactionSpecification.from_text(
                service_code=self.service_code,
                transaction_type=self.type,
                transaction_number=self.number,
                text=self.text,
            )


@define
class Transaction:
    """Transaction contains an OCR Giro transaction.

    Transactions are found in assignments with the service code
    :attr:`~netsgiro.ServiceCode.OCR_GIRO` type, which are only
    created by Nets.
    """

    #: The service code. One of :class:`~netsgiro.ServiceCode`.
    service_code: ServiceCode = field(converter=to_service_code)

    #: The transaction type. One of :class:`~TransactionType`.
    type: TransactionType = field(converter=to_transaction_type)

    #: Transaction number. Unique and ordered within an assignment.
    number: int = field(validator=instance_of(int))

    #: Nets' processing date.
    date: datetime.date = field(validator=instance_of(datetime.date))

    #: Transaction amount in NOK with two decimals.
    amount: Decimal = field(converter=Decimal)

    #: KID number to identify the customer and invoice.
    kid: Optional[str] = field(validator=optional(instance_of(str)))

    #: The value depends on the payment method.
    reference: Optional[str] = field(validator=optional(instance_of(str)))

    #: Up to 40 chars of free text from the payment terminal.
    text: Optional[str] = field(validator=optional(instance_of(str)))

    #: Used for OCR Giro.
    centre_id: Optional[str] = field(validator=optional(str_of_length(2)))

    #: Used for OCR Giro.
    day_code: Optional[int] = field(validator=optional(instance_of(int)))

    #: Used for OCR Giro.
    partial_settlement_number: Optional[int] = field(validator=optional(instance_of(int)))

    #: Used for OCR Giro.
    partial_settlement_serial_number: Optional[str] = field(validator=optional(str_of_length(5)))

    #: Used for OCR Giro.
    sign: Optional[str] = field(validator=optional(str_of_length(1)))

    #: Used for OCR Giro.
    form_number: Optional[str] = field(validator=optional(str_of_length(10)))

    #: Used for OCR Giro.
    bank_date: Optional[datetime.date] = field(validator=optional(instance_of(datetime.date)))

    #: Used for OCR Giro.
    debit_account: Optional[str] = field(validator=optional(str_of_length(11)))

    _filler: Optional[str] = field(validator=optional(str_of_length(7)))

    @property
    def amount_in_cents(self) -> int:
        """Transaction amount in NOK cents."""
        return int(self.amount * 100)

    @classmethod
    def from_records(cls, records: List[TR]) -> 'Transaction':
        """Build a Transaction object from a list of record objects."""
        amount_item_1 = records.pop(0)
        assert isinstance(amount_item_1, TransactionAmountItem1)
        amount_item_2 = records.pop(0)
        assert isinstance(amount_item_2, TransactionAmountItem2)

        if len(records) == 1 and isinstance(records[0], TransactionAmountItem3):
            text = records[0].text
        else:
            text = None

        return cls(
            service_code=amount_item_1.service_code,
            type=amount_item_1.transaction_type,
            number=amount_item_1.transaction_number,
            date=amount_item_1.nets_date,
            amount=Decimal(amount_item_1.amount) / 100,
            kid=amount_item_1.kid,
            reference=amount_item_2.reference,
            text=text,
            centre_id=amount_item_1.centre_id,
            day_code=amount_item_1.day_code,
            partial_settlement_number=amount_item_1.partial_settlement_number,
            partial_settlement_serial_number=amount_item_1.partial_settlement_serial_number,
            sign=amount_item_1.sign,
            form_number=amount_item_2.form_number,
            bank_date=amount_item_2.bank_date,
            debit_account=amount_item_2.debit_account,
            filler=amount_item_2._filler,
        )

    def to_records(self) -> Iterable[TransactionAmountItems]:
        """Convert the transaction to a list of records."""
        yield TransactionAmountItem1(
            service_code=self.service_code,
            transaction_type=self.type,
            transaction_number=self.number,
            nets_date=self.date,
            amount=self.amount_in_cents,
            kid=self.kid,
            centre_id=self.centre_id,
            day_code=self.day_code,
            partial_settlement_number=self.partial_settlement_number,
            partial_settlement_serial_number=self.partial_settlement_serial_number,
            sign=self.sign,
        )
        yield TransactionAmountItem2(
            service_code=self.service_code,
            transaction_type=self.type,
            transaction_number=self.number,
            reference=self.reference,
            form_number=self.form_number,
            bank_date=self.bank_date,
            debit_account=self.debit_account,
            filler=self._filler,
        )

        if self.type in (
            TransactionType.REVERSING_WITH_TEXT,
            TransactionType.PURCHASE_WITH_TEXT,
        ):
            yield TransactionAmountItem3(
                service_code=self.service_code,
                transaction_type=self.type,
                transaction_number=self.number,
                text=self.text,
            )


def parse(data: str) -> Transmission:
    """Parse an OCR file into a Transmission object."""
    return Transmission.from_records(records_parse(data))
