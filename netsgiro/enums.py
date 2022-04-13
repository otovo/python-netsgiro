"""Enums for all codes used in OCR files."""

from enum import IntEnum
from typing import List

__all__: List[str] = [
    'ServiceCode',
    'RecordType',
    'AssignmentType',
    'TransactionType',
    'AvtaleGiroRegistrationType',
]


class ServiceCode(IntEnum):
    """Service codes tell which Nets service the record applies to."""

    #: Used for the transmission start and end record.
    NONE = 0

    #: Used for all OCR Giro records.
    OCR_GIRO = 9

    #: Used for all AvtaleGiro records.
    AVTALEGIRO = 21


class RecordType(IntEnum):
    """Record types tell what type of record this is."""

    #: See :class:`netsgiro.TransmissionStart`.
    TRANSMISSION_START = 10

    #: See :class:`netsgiro.AssignmentStart`.
    ASSIGNMENT_START = 20

    #: See :class:`netsgiro.TransactionAmountItem1`.
    TRANSACTION_AMOUNT_ITEM_1 = 30

    #: See :class:`netsgiro.TransactionAmountItem2`.
    TRANSACTION_AMOUNT_ITEM_2 = 31

    #: See :class:`netsgiro.TransactionAmountItem3`.
    TRANSACTION_AMOUNT_ITEM_3 = 32

    #: See :class:`netsgiro.TransactionSpecification`.
    TRANSACTION_SPECIFICATION = 49

    #: See :class:`netsgiro.TransactionAgreements`.
    TRANSACTION_AGREEMENTS = 70

    #: See :class:`netsgiro.AssignmentEnd`.
    ASSIGNMENT_END = 88

    #: See :class:`netsgiro.TransmissionEnd`.
    TRANSMISSION_END = 89


class AssignmentType(IntEnum):
    """Assignment types tell what type of assignment this is."""

    #: Used both for AvtaleGiro payment requests and OCR Giro transactions.
    TRANSACTIONS = 0

    #: Used for AvtaleGiro agreement updates.
    AVTALEGIRO_AGREEMENTS = 24

    #: Used for AvtaleGiro cancellations.
    AVTALEGIRO_CANCELLATIONS = 36


class TransactionType(IntEnum):
    """Assignment types tell what type of transaction this is."""

    #: Used for OCR Giro.
    FROM_GIRO_DEBITED_ACCOUNT = 10
    #: Used for OCR Giro.
    FROM_STANDING_ORDERS = 11
    #: Used for OCR Giro.
    FROM_DIRECT_REMITTANCE = 12
    #: Used for OCR Giro.
    FROM_BUSINESS_TERMINAL_GIRO = 13
    #: Used for OCR Giro.
    FROM_COUNTER_GIRO = 14
    #: Used for OCR Giro.
    FROM_AVTALEGIRO = 15
    #: Used for OCR Giro.
    FROM_TELEGIRO = 16
    #: Used for OCR Giro.
    FROM_CASH_GIRO = 17

    #: Used for OCR Giro.
    REVERSING_WITH_KID = 18
    #: Used for OCR Giro.
    PURCHASE_WITH_KID = 19
    #: Used for OCR Giro.
    REVERSING_WITH_TEXT = 20
    #: Used for OCR Giro.
    #:
    #: .. note::
    #:     The value ``21`` is used for both :attr:`PURCHASE_WITH_TEXT` and
    #:     :attr:`AVTALEGIRO_WITH_BANK_NOTIFICATION`. The enum
    #:     representation will be ``<PURCHASE_WITH_TEXT: 21>`` in either case.
    PURCHASE_WITH_TEXT = 21

    #: Used for AvtaleGiro when you want to notify the payer yourself.
    AVTALEGIRO_WITH_PAYEE_NOTIFICATION = 2
    #: Used for AvtaleGiro when you want the bank to notify the payer.
    AVTALEGIRO_WITH_BANK_NOTIFICATION = 21
    #: Used for transactions that are part of an AvtaleGiro cancellation
    #: assignment.
    AVTALEGIRO_CANCELLATION = 93
    #: Used by Nets for updates to AvtaleGiro agreeements.
    AVTALEGIRO_AGREEMENT = 94


class AvtaleGiroRegistrationType(IntEnum):
    """AvtaleGiro registration types tell what kind of update this is."""

    #: Used when the AvtaleGiro agreement assignment contains all currently
    #: active agreements.
    ACTIVE_AGREEMENT = 0

    #: Used when the AvtaleGiro agreement assignment contains only changes,
    #: and the current agreement is new or updated.
    NEW_OR_UPDATED_AGREEMENT = 1

    #: Used when the AvtaleGiro agreement assignment contains only changes,
    #: and the current agreement has been deleted.
    DELETED_AGREEMENT = 2
