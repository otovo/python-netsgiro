import collections
from decimal import Decimal
from typing import List

import attr

import netsgiro
from netsgiro.records import Record


__all__ = [
    'Transmission',
    'Assignment',
    'Transaction',
    'parse',
]


class Serializable:
    def to_dict(self):
        return attr.asdict(self)


@attr.s
class Transmission(Serializable):
    number = attr.ib()
    data_transmitter = attr.ib()
    data_recipient = attr.ib()

    # TODO For AvtaleGiro payment request, this should be the earliest due date
    nets_date = attr.ib()

    assignments = attr.ib(default=[])

    @classmethod
    def from_records(cls, records: List[Record]) -> 'Transmission':
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
            nets_date=end.nets_date,
            assignments=get_assignments(body),
        )


@attr.s
class Assignment(Serializable):
    service_code = attr.ib(convert=netsgiro.ServiceCode)
    type = attr.ib(convert=netsgiro.AssignmentType)
    agreement_id = attr.ib()
    number = attr.ib()
    account = attr.ib()

    transactions = attr.ib(default=[])

    @classmethod
    def from_records(cls, records: List[Record]) -> 'Assignment':
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
            transactions=get_transactions(body)
        )


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
class Transaction(Serializable):
    service_code = attr.ib(convert=netsgiro.ServiceCode)
    type = attr.ib(convert=netsgiro.TransactionType)
    number = attr.ib()
    nets_date = attr.ib()
    amount = attr.ib(convert=Decimal)
    kid = attr.ib()
    reference = attr.ib()
    text = attr.ib()

    # Specific to AvtaleGiro
    payer_name = attr.ib()

    @property
    def amount_in_cents(self):
        return int(self.amount * 100)

    @classmethod
    def from_records(cls, records: List[Record]) -> 'Transaction':
        amount_item_1 = records.pop(0)
        assert isinstance(amount_item_1, netsgiro.TransactionAmountItem1)
        amount_item_2 = records.pop(0)
        assert isinstance(amount_item_2, netsgiro.TransactionAmountItem2)

        # TODO If service_code is OCR_GIRO and transaction_type is 20 or 21,
        # pop amount_item_3 here
        text = get_avtalegiro_specification_text(records)

        return cls(
            service_code=amount_item_1.service_code,
            type=amount_item_1.transaction_type,
            number=amount_item_1.transaction_number,
            nets_date=amount_item_1.nets_date,
            amount=Decimal(amount_item_1.amount) / 100,
            kid=amount_item_1.kid,
            reference=amount_item_2.reference,
            text=text,

            # Specific to AvtaleGiro
            payer_name=amount_item_2.payer_name,
        )


def get_transactions(records: List[Record]) -> List[Transaction]:
    transactions = collections.OrderedDict()

    for record in records:
        if record.transaction_number not in transactions:
            transactions[record.transaction_number] = []
        transactions[record.transaction_number].append(record)

    return [Transaction.from_records(rs) for rs in transactions.values()]


def get_avtalegiro_specification_text(records: List[Record]) -> str:
    MAX_LINES = 42
    MAX_COLUMNS = 2
    MAX_RECORDS = MAX_LINES * MAX_COLUMNS

    if len(records) > MAX_RECORDS:
        raise ValueError(
            'Max {} specification records allowed, got {}'
            .format(MAX_RECORDS, len(records)))

    tuples = sorted([
        (r.line_number, r.column_number, r)
        for r in records
    ])

    text = ''
    for _, column, specification in tuples:
        text += specification.text
        if column == MAX_COLUMNS:
            text += '\n'

    return text


def parse(data: str) -> Transmission:
    records = netsgiro.get_records(data)
    return Transmission.from_records(records)
