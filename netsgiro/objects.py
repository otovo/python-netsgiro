import collections
import datetime
from decimal import Decimal
from typing import Iterable, List, Optional

import attr

import netsgiro
from netsgiro.records import Record


__all__ = [
    'Transmission',
    'Assignment',
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
    number = attr.ib()

    #: Data transmitter's Nets ID. String of 8 digits.
    data_transmitter = attr.ib()

    #: Data recipient's Nets ID. String of 8 digits.
    data_recipient = attr.ib()

    #: For OCR Giro files from Nets, this is Nets' processing date.
    #:
    #: For AvtaleGiro payment request, the earliest due date in the
    #: transmission is automatically used.
    date = attr.ib(default=None)

    #: List of assignments.
    assignments = attr.ib(default=attr.Factory(list), repr=False)

    @classmethod
    def from_records(cls, records: List[Record]) -> 'Transmission':
        """Build a Transmission object from a list of record objects."""
        if len(records) < 2:
            raise ValueError(
                'At least 2 records required, got {}'.format(len(records)))

        start, body, end = records[0], records[1:-1], records[-1]

        assert isinstance(start, netsgiro.TransmissionStart)
        assert isinstance(end, netsgiro.TransmissionEnd)

        return cls(
            number=start.transmission_number,
            data_transmitter=start.data_transmitter,
            data_recipient=start.data_recipient,
            date=end.nets_date,
            assignments=get_assignments(body),
        )

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
        return netsgiro.TransmissionStart(
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

        return netsgiro.TransmissionEnd(
            service_code=netsgiro.ServiceCode.NONE,
            num_transactions=self.get_num_transactions(),
            num_records=self.get_num_records(),
            total_amount=int(self.get_total_amount() * 100),
            nets_date=date,
        )

    def add_assignment(
            self, *,
            service_code, assignment_type, agreement_id=None, number, account,
            date=None
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

    #: Used for OCR Giro.
    #:
    #: The payee's agreement ID with Nets. String of 9 digits.
    agreement_id = attr.ib()

    #: The assignment number. String of 7 digits.
    number = attr.ib()

    #: The payee's bank account. String of 11 digits.
    account = attr.ib()

    #: Used for OCR Giro.
    #:
    #: The date the assignment was generated by Nets.
    date = attr.ib(default=None)

    #: List of transactions.
    transactions = attr.ib(default=attr.Factory(list), repr=False)

    _next_transaction_number = 1

    @classmethod
    def from_records(cls, records: List[Record]) -> 'Assignment':
        """Build a Transmission object from a list of record objects."""
        if len(records) < 2:
            raise ValueError(
                'At least 2 records required, got {}'.format(len(records)))

        start, body, end = records[0], records[1:-1], records[-1]

        assert isinstance(start, netsgiro.AssignmentStart)
        assert isinstance(end, netsgiro.AssignmentEnd)

        return cls(
            service_code=start.service_code,
            type=start.assignment_type,
            agreement_id=start.agreement_id,
            number=start.assignment_number,
            account=start.assignment_account,
            date=end.nets_date,
            transactions=get_transactions(body)
        )

    def to_records(self) -> Iterable[Record]:
        """Convert the assignment to a list of records."""
        yield self._get_start_record()
        for transaction in self.transactions:
            yield from transaction.to_records()
        yield self._get_end_record()

    def _get_start_record(self) -> Record:
        return netsgiro.AssignmentStart(
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

        return netsgiro.AssignmentEnd(
            service_code=self.service_code,
            assignment_type=self.type,
            num_transactions=self.get_num_transactions(),
            num_records=self.get_num_records(),
            total_amount=int(self.get_total_amount() * 100),
            **dates
        )

    def add_payment_request(
            self, *,
            kid, due_date, amount,
            reference=None, payer_name=None, bank_notification=None
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
            kid, due_date, amount,
            reference=None, payer_name=None, bank_notification=None
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

        transaction = Transaction(
            service_code=self.service_code,
            type=transaction_type,
            number=number,
            date=due_date,
            amount=amount,
            kid=kid,
            reference=reference,
            text=text,

            centre_id=None,
            day_code=None,
            partial_settlement_number=None,
            partial_settlement_serial_number=None,
            sign=None,
            form_number=None,
            bank_date=None,
            debit_account=None,
            filler=None,

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
        return sum(
            transaction.amount
            for transaction in self.transactions)

    def get_earliest_transaction_date(self) -> Optional[datetime.date]:
        """Get earliest date from the assignment's transactions."""
        if not self.transactions:
            return None
        return min(transaction.date for transaction in self.transactions)

    def get_latest_transaction_date(self) -> Optional[datetime.date]:
        """Get latest date from the assignment's transactions."""
        if not self.transactions:
            return None
        return max(transaction.date for transaction in self.transactions)


def get_assignments(records: List[Record]) -> List[Assignment]:
    assignments = collections.OrderedDict()

    current_assignment_number = None
    for record in records:
        if isinstance(record, netsgiro.AssignmentStart):
            current_assignment_number = record.assignment_number
            assignments[current_assignment_number] = []
        if current_assignment_number is None:
            raise ValueError(
                'Expected AssignmentStart record, got {!r}'.format(record))
        assignments[current_assignment_number].append(record)
        if isinstance(record, netsgiro.AssignmentEnd):
            current_assignment_number = None

    return [Assignment.from_records(rs) for rs in assignments.values()]


@attr.s
class Transaction:
    """Transaction is the bottom-level object.

    To create a transaction, you will normally use the helper methods on
    :class:`~netsgiro.Assignment`, e.g.
    :meth:`~netsgiro.Assignment.add_payment_request` and
    :meth:`~netsgiro.Assignment.add_payment_cancellation`.
    """

    #: The service code. One of :class:`~netsgiro.ServiceCode`.
    service_code = attr.ib(convert=netsgiro.ServiceCode)

    #: The transaction type. One of :class:`~netsgiro.TransactionType`.
    type = attr.ib(convert=netsgiro.TransactionType)

    #: Transaction number. Unique and ordered within an assignment.
    number = attr.ib()

    #: For OCR Giro, the value is Nets' processing date.
    #:
    #: For AvtaleGiro, this is the payment due date.
    date = attr.ib()

    #: Transaction amount in NOK with two decimals.
    amount = attr.ib(convert=Decimal)

    #: KID number to identify the customer and invoice.
    kid = attr.ib()

    #: For OCR Giro, the value depends on the payment method.
    #:
    #: For AvtaleGiro, this is a specification line that will, if set, be
    #: displayed on the payers account statement. Alphanumeric, max 25 chars.
    reference = attr.ib()

    #: For OCR Giro, the value is up to 40 chars of free text from the payment
    #: terminal.
    #:
    #: For AvtaleGiro, this is up to 42 lines of 80 chars each of free text
    #: used by the bank to notify the payer about the payment request. It is
    #: not used if the payee is responsible for notifying the payer.
    text = attr.ib()

    # --- Specific to OCR Giro

    #: Used for OCR Giro.
    centre_id = attr.ib()

    #: Used for OCR Giro.
    day_code = attr.ib()

    #: Used for OCR Giro.
    partial_settlement_number = attr.ib()

    #: Used for OCR Giro.
    partial_settlement_serial_number = attr.ib()

    #: Used for OCR Giro.
    sign = attr.ib()

    #: Used for OCR Giro.
    form_number = attr.ib()

    #: Used for OCR Giro.
    bank_date = attr.ib()

    #: Used for OCR Giro.
    debit_account = attr.ib()

    _filler = attr.ib()

    # --- Specific to AvtaleGiro

    #: Used for AvtaleGiro.
    #:
    #: The value is only used to help the payee cross-reference reports from
    #: Nets with their own records. It is not visible to the payer.
    payer_name = attr.ib()

    @property
    def amount_in_cents(self) -> int:
        """Transaction amount in NOK cents."""
        return int(self.amount * 100)

    @classmethod
    def from_records(cls, records: List[Record]) -> 'Transaction':
        amount_item_1 = records.pop(0)
        assert isinstance(amount_item_1, netsgiro.TransactionAmountItem1)
        amount_item_2 = records.pop(0)
        assert isinstance(amount_item_2, netsgiro.TransactionAmountItem2)

        if amount_item_1.service_code == netsgiro.ServiceCode.OCR_GIRO:
            text = get_ocr_giro_text(records)
        elif amount_item_1.service_code == netsgiro.ServiceCode.AVTALEGIRO:
            text = netsgiro.TransactionSpecification.to_text(records)
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

            # Specific to OCR Giro
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

            # Specific to AvtaleGiro
            payer_name=amount_item_2.payer_name,
        )

    def to_records(self) -> Iterable[Record]:
        """Convert the transaction to a list of records."""
        yield netsgiro.TransactionAmountItem1(
            service_code=self.service_code,
            transaction_type=self.type,
            transaction_number=self.number,

            nets_date=self.date,
            amount=self.amount_in_cents,
            kid=self.kid,

            # Only OCR Giro
            centre_id=self.centre_id,
            day_code=self.day_code,
            partial_settlement_number=self.partial_settlement_number,
            partial_settlement_serial_number=(
                self.partial_settlement_serial_number),
            sign=self.sign,
        )
        yield netsgiro.TransactionAmountItem2(
            service_code=self.service_code,
            transaction_type=self.type,
            transaction_number=self.number,

            reference=self.reference,

            # Only OCR Giro
            form_number=self.form_number,
            bank_date=self.bank_date,
            debit_account=self.debit_account,
            filler=self._filler,

            # Only AvtaleGiro
            payer_name=self.payer_name,
        )

        if (
                self.service_code == netsgiro.ServiceCode.OCR_GIRO and
                self.type in (
                    netsgiro.TransactionType.REVERSING_WITH_TEXT,
                    netsgiro.TransactionType.PURCHASE_WITH_TEXT)):
            yield netsgiro.TransactionAmountItem3(
                service_code=self.service_code,
                transaction_type=self.type,
                transaction_number=self.number,

                text=self.text,
            )

        if (
                self.service_code == netsgiro.ServiceCode.AVTALEGIRO and
                self.type == (
                    netsgiro.TransactionType.AVTALEGIRO_WITH_BANK_NOTIFICATION)
                ):
            yield from netsgiro.TransactionSpecification.from_text(
                service_code=self.service_code,
                transaction_type=self.type,
                transaction_number=self.number,

                text=self.text,
            )

        # TODO Support constructing AvtaleGiroAgreement records


def get_transactions(records: List[Record]) -> List[Transaction]:
    transactions = collections.OrderedDict()

    for record in records:
        if record.transaction_number not in transactions:
            transactions[record.transaction_number] = []
        transactions[record.transaction_number].append(record)

    return [Transaction.from_records(rs) for rs in transactions.values()]


def get_ocr_giro_text(records: List[Record]) -> str:
    if (
            len(records) == 1 and
            isinstance(records[0], netsgiro.TransactionAmountItem3)):
        return records[0].text


def parse(data: str) -> Transmission:
    records = netsgiro.get_records(data)
    return Transmission.from_records(records)
