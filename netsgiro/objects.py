"""The higher-level objects API."""

import collections
import datetime
from decimal import Decimal
from typing import Iterable, List, Mapping, Optional, Union

import attr
from attr.validators import instance_of, optional

import netsgiro
import netsgiro.records
from netsgiro.records import Record
from netsgiro.validators import str_of_length


__all__ = [
    'Transmission',
    'Assignment',
    'Agreement',
    'PaymentRequest',
    'Transaction',
    'parse',
]


@attr.s
class Transmission:
    """Transmission is the top-level object.

    An OCR file contains a single transmission. The transmission can contain
    multiple :class:`~netsgiro.Assignment` objects of various types.
    """

    #: Data transmitters unique enumeration of the transmission. String of 7
    #: digits.
    number = attr.ib(validator=str_of_length(7))

    #: Data transmitter's Nets ID. String of 8 digits.
    data_transmitter = attr.ib(validator=str_of_length(8))

    #: Data recipient's Nets ID. String of 8 digits.
    data_recipient = attr.ib(validator=str_of_length(8))

    #: For OCR Giro files from Nets, this is Nets' processing date.
    #:
    #: For AvtaleGiro payment request, the earliest due date in the
    #: transmission is automatically used.
    date = attr.ib(
        default=None, validator=optional(instance_of(datetime.date)))

    #: List of assignments.
    assignments = attr.ib(default=attr.Factory(list), repr=False)

    @classmethod
    def from_records(cls, records: List[Record]) -> 'Transmission':
        """Build a Transmission object from a list of record objects."""
        if len(records) < 2:
            raise ValueError(
                'At least 2 records required, got {}'.format(len(records)))

        start, body, end = records[0], records[1:-1], records[-1]

        assert isinstance(start, netsgiro.records.TransmissionStart)
        assert isinstance(end, netsgiro.records.TransmissionEnd)

        return cls(
            number=start.transmission_number,
            data_transmitter=start.data_transmitter,
            data_recipient=start.data_recipient,
            date=end.nets_date,
            assignments=cls._get_assignments(body),
        )

    @staticmethod
    def _get_assignments(records: List[Record]) -> List['Assignment']:
        assignments = collections.OrderedDict()

        current_assignment_number = None
        for record in records:
            if isinstance(record, netsgiro.records.AssignmentStart):
                current_assignment_number = record.assignment_number
                assignments[current_assignment_number] = []
            if current_assignment_number is None:
                raise ValueError(
                    'Expected AssignmentStart record, got {!r}'.format(record))
            assignments[current_assignment_number].append(record)
            if isinstance(record, netsgiro.records.AssignmentEnd):
                current_assignment_number = None

        return [Assignment.from_records(rs) for rs in assignments.values()]

    def to_ocr(self) -> str:
        """Convert the transmission to an OCR string."""
        lines = [record.to_ocr() for record in self.to_records()]
        return '\n'.join(lines)

    def to_records(self) -> Iterable[Record]:
        """Convert the transmission to a list of records."""
        yield self._get_start_record()
        for assignment in self.assignments:
            yield from assignment.to_records()
        yield self._get_end_record()

    def _get_start_record(self) -> Record:
        return netsgiro.records.TransmissionStart(
            service_code=netsgiro.ServiceCode.NONE,
            transmission_number=self.number,
            data_transmitter=self.data_transmitter,
            data_recipient=self.data_recipient,
        )

    def _get_end_record(self) -> Record:
        avtalegiro_payment_request = all(
            assignment.service_code == netsgiro.ServiceCode.AVTALEGIRO and
            assignment.type in (
                netsgiro.AssignmentType.TRANSACTIONS,
                netsgiro.AssignmentType.AVTALEGIRO_CANCELLATIONS,
            )
            for assignment in self.assignments)
        if self.assignments and avtalegiro_payment_request:
            date = min(
                assignment.get_earliest_transaction_date()
                for assignment in self.assignments)
        else:
            date = self.date

        return netsgiro.records.TransmissionEnd(
            service_code=netsgiro.ServiceCode.NONE,
            num_transactions=self.get_num_transactions(),
            num_records=self.get_num_records(),
            total_amount=int(self.get_total_amount() * 100),
            nets_date=date,
        )

    def add_assignment(
            self, *,
            service_code: netsgiro.ServiceCode,
            assignment_type: netsgiro.AssignmentType,
            agreement_id: Optional[str]=None,
            number: str,
            account: str,
            date: Optional[datetime.date]=None
            ) -> 'Assignment':
        """Add an assignment to the tranmission."""

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
        return sum(
            assignment.get_num_transactions()
            for assignment in self.assignments)

    def get_num_records(self) -> int:
        """Get number of records in the transmission.

        Includes the transmission's start and end record.
        """
        return 2 + sum(
            assignment.get_num_records()
            for assignment in self.assignments)

    def get_total_amount(self) -> Decimal:
        """Get the total amount from all transactions in the transmission."""
        return sum(
            assignment.get_total_amount()
            for assignment in self.assignments)


@attr.s
class Assignment:
    """An Assignment groups multiple transactions within a transmission.

    Use :meth:`netsgiro.Transmission.add_assignment` to create assignments.
    """

    #: The service code. One of :class:`~netsgiro.ServiceCode`.
    service_code = attr.ib(convert=netsgiro.ServiceCode)

    #: The transaction type. One of :class:`~netsgiro.TransactionType`.
    type = attr.ib(convert=netsgiro.AssignmentType)

    #: The assignment number. String of 7 digits.
    number = attr.ib(validator=str_of_length(7))

    #: The payee's bank account. String of 11 digits.
    account = attr.ib(validator=str_of_length(11))

    #: Used for OCR Giro.
    #:
    #: The payee's agreement ID with Nets. String of 9 digits.
    agreement_id = attr.ib(default=None, validator=optional(str_of_length(9)))

    #: Used for OCR Giro.
    #:
    #: The date the assignment was generated by Nets.
    date = attr.ib(
        default=None, validator=optional(instance_of(datetime.date)))

    #: List of transaction objects, like :class:`~netsgiro.Agreement`,
    #: :class:`~netsgiro.PaymentRequest`, :class:`~netsgiro.Transaction`.
    transactions = attr.ib(default=attr.Factory(list), repr=False)

    _next_transaction_number = 1

    @classmethod
    def from_records(cls, records: List[Record]) -> 'Assignment':
        """Build an Assignment object from a list of record objects."""
        if len(records) < 2:
            raise ValueError(
                'At least 2 records required, got {}'.format(len(records)))

        start, body, end = records[0], records[1:-1], records[-1]

        assert isinstance(start, netsgiro.records.AssignmentStart)
        assert isinstance(end, netsgiro.records.AssignmentEnd)

        if start.service_code == netsgiro.ServiceCode.AVTALEGIRO:
            if (
                    start.assignment_type ==
                    netsgiro.AssignmentType.AVTALEGIRO_AGREEMENTS):
                transactions = cls._get_agreements(body)
            else:
                transactions = cls._get_payment_requests(body)
        elif start.service_code == netsgiro.ServiceCode.OCR_GIRO:
            transactions = cls._get_transactions(body)
        else:
            raise ValueError(
                'Unknown service code: {}'.format(start.service_code))

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
    def _get_agreements(records: List[Record]) -> List['Agreement']:
        return [Agreement.from_records([r]) for r in records]

    @classmethod
    def _get_payment_requests(
            cls, records: List[Record]) -> List['PaymentRequest']:
        transactions = cls._group_by_transaction_number(records)
        return [
            PaymentRequest.from_records(rs) for rs in transactions.values()]

    @classmethod
    def _get_transactions(cls, records: List[Record]) -> List['Transaction']:
        transactions = cls._group_by_transaction_number(records)
        return [Transaction.from_records(rs) for rs in transactions.values()]

    @staticmethod
    def _group_by_transaction_number(
            records: List[Record]) -> Mapping[int, List[Record]]:
        transactions = collections.OrderedDict()

        for record in records:
            if record.transaction_number not in transactions:
                transactions[record.transaction_number] = []
            transactions[record.transaction_number].append(record)

        return transactions

    def to_records(self) -> Iterable[Record]:
        """Convert the assignment to a list of records."""
        yield self._get_start_record()
        for transaction in self.transactions:
            yield from transaction.to_records()
        yield self._get_end_record()

    def _get_start_record(self) -> Record:
        return netsgiro.records.AssignmentStart(
            service_code=self.service_code,
            assignment_type=self.type,
            assignment_number=self.number,
            assignment_account=self.account,
            agreement_id=self.agreement_id,
        )

    def _get_end_record(self) -> Record:
        if self.service_code == netsgiro.ServiceCode.OCR_GIRO:
            dates = {
                'nets_date_1': self.date,
                'nets_date_2': self.get_earliest_transaction_date(),
                'nets_date_3': self.get_latest_transaction_date(),
            }
        elif self.service_code == netsgiro.ServiceCode.AVTALEGIRO:
            dates = {
                'nets_date_1': self.get_earliest_transaction_date(),
                'nets_date_2': self.get_latest_transaction_date(),
            }
        else:
            raise ValueError(
                'Unhandled service code: {}'.format(self.service_code))

        return netsgiro.records.AssignmentEnd(
            service_code=self.service_code,
            assignment_type=self.type,
            num_transactions=self.get_num_transactions(),
            num_records=self.get_num_records(),
            total_amount=int(self.get_total_amount() * 100),
            **dates
        )

    def add_payment_request(
            self, *,
            kid: str,
            due_date: datetime.date,
            amount: Decimal,
            reference: Optional[str]=None,
            payer_name: Optional[str]=None,
            bank_notification: Union[bool, str]=False
            ) -> 'Transaction':
        """Add an AvtaleGiro payment request to the assignment.

        The assignment must have service code
        :attr:`~netsgiro.ServiceCode.AVTALEGIRO` and assignment type
        :attr:`~netsgiro.AssignmentType.TRANSACTIONS`.
        """

        assert self.service_code == netsgiro.ServiceCode.AVTALEGIRO, (
            'Can only add payment requests to AvtaleGiro assignments')
        assert self.type == netsgiro.AssignmentType.TRANSACTIONS, (
            'Can only add payment requests to transaction assignments')

        if bank_notification:
            transaction_type = (
                netsgiro.TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION)
        else:
            transaction_type = (
                netsgiro.TransactionType.AVTALEGIRO_WITH_PAYEE_NOTIFICATION)

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
            self, *,
            kid: str,
            due_date: datetime.date,
            amount: Decimal,
            reference: Optional[str]=None,
            payer_name: Optional[str]=None,
            bank_notification: Union[bool, str]=False
            ) -> 'Transaction':
        """Add an AvtaleGiro cancellation to the assignment.

        The assignment must have service code
        :attr:`~netsgiro.ServiceCode.AVTALEGIRO` and assignment type
        :attr:`~netsgiro.AssignmentType.AVTALEGIRO_CANCELLATIONS`.

        Otherwise, the cancellation must be identical to the payment request it
        is cancelling.
        """

        assert self.service_code == netsgiro.ServiceCode.AVTALEGIRO, (
            'Can only add cancellation to AvtaleGiro assignments')
        assert self.type == netsgiro.AssignmentType.AVTALEGIRO_CANCELLATIONS, (
            'Can only add cancellation to cancellation assignments')

        return self._add_avtalegiro_transaction(
            transaction_type=netsgiro.TransactionType.AVTALEGIRO_CANCELLATION,
            kid=kid,
            due_date=due_date,
            amount=amount,
            reference=reference,
            payer_name=payer_name,
            bank_notification=bank_notification,
        )

    def _add_avtalegiro_transaction(
            self, *,
            transaction_type,
            kid, due_date, amount,
            reference=None, payer_name=None, bank_notification=None
            ) -> 'Transaction':

        if isinstance(bank_notification, str):
            text = bank_notification
        else:
            text = ''

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

        return 2 + sum(
            len(list(transaction.to_records()))
            for transaction in self.transactions)

    def get_total_amount(self) -> Decimal:
        """Get the total amount from all transactions in the assignment."""
        transactions = [
            transaction
            for transaction in self.transactions
            if hasattr(transaction, 'amount')]
        if not transactions:
            return Decimal(0)
        return sum(transaction.amount for transaction in transactions)

    def get_earliest_transaction_date(self) -> Optional[datetime.date]:
        """Get earliest date from the assignment's transactions."""
        transactions = [
            transaction
            for transaction in self.transactions
            if hasattr(transaction, 'date')]
        if not transactions:
            return None
        return min(transaction.date for transaction in transactions)

    def get_latest_transaction_date(self) -> Optional[datetime.date]:
        """Get latest date from the assignment's transactions."""
        transactions = [
            transaction
            for transaction in self.transactions
            if hasattr(transaction, 'date')]
        if not transactions:
            return None
        return max(transaction.date for transaction in transactions)


@attr.s
class Agreement:
    """Agreement contains an AvtaleGiro agreement update.

    Agreements are only found in assignments of the
    :attr:`~netsgiro.AssignmentType.AVTALEGIRO_AGREEMENTS` type, which are only
    created by Nets.
    """

    #: The service code. One of :class:`~netsgiro.ServiceCode`.
    service_code = attr.ib(convert=netsgiro.ServiceCode)

    #: Transaction number. Unique and ordered within an assignment.
    number = attr.ib(validator=instance_of(int))

    #: Type of agreement registration update.
    #: One of :class:`~netsgiro.AvtaleGiroRegistrationType`.
    registration_type = attr.ib(convert=netsgiro.AvtaleGiroRegistrationType)

    #: KID number to identify the customer and invoice.
    kid = attr.ib(validator=optional(instance_of(str)))

    #: Whether the payer wants notification about payment requests.
    notify = attr.ib(validator=instance_of(bool))

    TRANSACTION_TYPE = netsgiro.TransactionType.AVTALEGIRO_AGREEMENT

    @classmethod
    def from_records(cls, records: List[Record]) -> 'Agreement':
        """Build an Agreement object from a list of record objects."""

        assert len(records) == 1
        record = records[0]
        assert isinstance(record, netsgiro.records.AvtaleGiroAgreement)
        assert (
            record.transaction_type ==
            netsgiro.TransactionType.AVTALEGIRO_AGREEMENT)

        return cls(
            service_code=record.service_code,
            number=record.transaction_number,

            registration_type=record.registration_type,
            kid=record.kid,
            notify=record.notify,
        )

    def to_records(self) -> Iterable[Record]:
        """Convert the agreement to a list of records."""
        yield netsgiro.records.AvtaleGiroAgreement(
            service_code=self.service_code,
            transaction_type=self.TRANSACTION_TYPE,
            transaction_number=self.number,

            registration_type=self.registration_type,
            kid=self.kid,
            notify=self.notify,
        )


@attr.s
class PaymentRequest:
    """PaymentRequest contains an AvtaleGiro payment request or cancellation.

    To create a transaction, you will normally use the helper methods on
    :class:`~netsgiro.Assignment`:
    :meth:`~netsgiro.Assignment.add_payment_request` and
    :meth:`~netsgiro.Assignment.add_payment_cancellation`.
    """

    #: The service code. One of :class:`~netsgiro.ServiceCode`.
    service_code = attr.ib(convert=netsgiro.ServiceCode)

    #: The transaction type. One of :class:`~netsgiro.TransactionType`.
    type = attr.ib(convert=netsgiro.TransactionType)

    #: Transaction number. Unique and ordered within an assignment.
    number = attr.ib(validator=instance_of(int))

    #: The due date.
    date = attr.ib(validator=instance_of(datetime.date))

    #: Transaction amount in NOK with two decimals.
    amount = attr.ib(convert=Decimal)

    #: KID number to identify the customer and invoice.
    kid = attr.ib(validator=optional(instance_of(str)))

    #: This is a specification line that will, if set, be displayed on the
    #: payers account statement. Alphanumeric, max 25 chars.
    reference = attr.ib(validator=optional(instance_of(str)))

    #: This is up to 42 lines of 80 chars each of free text used by the bank to
    #: notify the payer about the payment request. It is not used if the payee
    #: is responsible for notifying the payer.
    text = attr.ib(validator=optional(instance_of(str)))

    #: The value is only used to help the payee cross-reference reports from
    #: Nets with their own records. It is not visible to the payer.
    payer_name = attr.ib(validator=optional(instance_of(str)))

    @property
    def amount_in_cents(self) -> int:
        """Transaction amount in NOK cents."""
        return int(self.amount * 100)

    @classmethod
    def from_records(cls, records: List[Record]) -> 'Transaction':
        """Build a Transaction object from a list of record objects."""
        amount_item_1 = records.pop(0)
        assert isinstance(
            amount_item_1, netsgiro.records.TransactionAmountItem1)
        amount_item_2 = records.pop(0)
        assert isinstance(
            amount_item_2, netsgiro.records.TransactionAmountItem2)

        text = netsgiro.records.TransactionSpecification.to_text(records)

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

    def to_records(self) -> Iterable[Record]:
        """Convert the transaction to a list of records."""
        yield netsgiro.records.TransactionAmountItem1(
            service_code=self.service_code,
            transaction_type=self.type,
            transaction_number=self.number,

            nets_date=self.date,
            amount=self.amount_in_cents,
            kid=self.kid,
        )
        yield netsgiro.records.TransactionAmountItem2(
            service_code=self.service_code,
            transaction_type=self.type,
            transaction_number=self.number,

            reference=self.reference,
            payer_name=self.payer_name,
        )

        if self.type == (
                netsgiro.TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION):
            yield from netsgiro.records.TransactionSpecification.from_text(
                service_code=self.service_code,
                transaction_type=self.type,
                transaction_number=self.number,

                text=self.text,
            )


@attr.s
class Transaction:
    """Transaction contains an OCR Giro transaction.

    Transactions are found in assignments with the service code
    :attr:`~netsgiro.ServiceCode.OCR_GIRO` type, which are only
    created by Nets.
    """

    #: The service code. One of :class:`~netsgiro.ServiceCode`.
    service_code = attr.ib(convert=netsgiro.ServiceCode)

    #: The transaction type. One of :class:`~netsgiro.TransactionType`.
    type = attr.ib(convert=netsgiro.TransactionType)

    #: Transaction number. Unique and ordered within an assignment.
    number = attr.ib(validator=instance_of(int))

    #: Nets' processing date.
    date = attr.ib(validator=instance_of(datetime.date))

    #: Transaction amount in NOK with two decimals.
    amount = attr.ib(convert=Decimal)

    #: KID number to identify the customer and invoice.
    kid = attr.ib(validator=optional(instance_of(str)))

    #: The value depends on the payment method.
    reference = attr.ib(validator=optional(instance_of(str)))

    #: Up to 40 chars of free text from the payment terminal.
    text = attr.ib(validator=optional(instance_of(str)))

    #: Used for OCR Giro.
    centre_id = attr.ib(validator=optional(str_of_length(2)))

    #: Used for OCR Giro.
    day_code = attr.ib(validator=optional(instance_of(int)))

    #: Used for OCR Giro.
    partial_settlement_number = attr.ib(validator=optional(instance_of(int)))

    #: Used for OCR Giro.
    partial_settlement_serial_number = attr.ib(
        validator=optional(str_of_length(5)))

    #: Used for OCR Giro.
    sign = attr.ib(validator=optional(str_of_length(1)))

    #: Used for OCR Giro.
    form_number = attr.ib(validator=optional(str_of_length(10)))

    #: Used for OCR Giro.
    bank_date = attr.ib(validator=optional(instance_of(datetime.date)))

    #: Used for OCR Giro.
    debit_account = attr.ib(validator=optional(str_of_length(11)))

    _filler = attr.ib(validator=optional(str_of_length(7)))

    @property
    def amount_in_cents(self) -> int:
        """Transaction amount in NOK cents."""
        return int(self.amount * 100)

    @classmethod
    def from_records(cls, records: List[Record]) -> 'Transaction':
        """Build a Transaction object from a list of record objects."""
        amount_item_1 = records.pop(0)
        assert isinstance(
            amount_item_1, netsgiro.records.TransactionAmountItem1)
        amount_item_2 = records.pop(0)
        assert isinstance(
            amount_item_2, netsgiro.records.TransactionAmountItem2)

        if (
                len(records) == 1 and
                isinstance(
                    records[0], netsgiro.records.TransactionAmountItem3)):
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
            partial_settlement_serial_number=(
                amount_item_1.partial_settlement_serial_number),
            sign=amount_item_1.sign,
            form_number=amount_item_2.form_number,
            bank_date=amount_item_2.bank_date,
            debit_account=amount_item_2.debit_account,
            filler=amount_item_2._filler,
        )

    def to_records(self) -> Iterable[Record]:
        """Convert the transaction to a list of records."""
        yield netsgiro.records.TransactionAmountItem1(
            service_code=self.service_code,
            transaction_type=self.type,
            transaction_number=self.number,

            nets_date=self.date,
            amount=self.amount_in_cents,
            kid=self.kid,

            centre_id=self.centre_id,
            day_code=self.day_code,
            partial_settlement_number=self.partial_settlement_number,
            partial_settlement_serial_number=(
                self.partial_settlement_serial_number),
            sign=self.sign,
        )
        yield netsgiro.records.TransactionAmountItem2(
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
                netsgiro.TransactionType.REVERSING_WITH_TEXT,
                netsgiro.TransactionType.PURCHASE_WITH_TEXT):
            yield netsgiro.records.TransactionAmountItem3(
                service_code=self.service_code,
                transaction_type=self.type,
                transaction_number=self.number,

                text=self.text,
            )


def parse(data: str) -> Transmission:
    """Parse an OCR file into a Transmission object."""
    records = netsgiro.records.parse(data)
    return Transmission.from_records(records)
