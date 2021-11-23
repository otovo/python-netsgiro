==========
Quickstart
==========

The following examples takes you through the flow from payers signing up for
AvtaleGiro to receiving payments.

See the :doc:`objects API reference <objects>` for details on the API and
data fields used in the examples below.


Parsing AvtaleGiro agreements
=============================

To parse an OCR file, you must first read the contents of the OCR file. It
should be decoded using the ISO-8859-1 encoding::

    with open('my-ocr-file.txt', 'r', encoding='iso-8859-1') as fh:
        data = fh.read()

For the purpose of the following example we use the following input data:

>>> data = """
... NY000010000080801091949000102000000000000000000000000000000000000000000000000000
... NY212420000000000000000299991042764000000000000000000000000000000000000000000000
... NY21947000000011          000112000507155J00000000000000000000000000000000000000
... NY21947000000021          001006300507304N00000000000000000000000000000000000000
... NY21947000000031          001020200507462J00000000000000000000000000000000000000
... NY21947000000041          001026300507518J00000000000000000000000000000000000000
... NY21947000000051          001044400507783J00000000000000000000000000000000000000
... NY21947000000061          001045000507792N00000000000000000000000000000000000000
... NY21947000000071          001057800507922N00000000000000000000000000000000000000
... NY21947000000081          001060300509570J00000000000000000000000000000000000000
... NY21947000000091          001087600508176J00000000000000000000000000000000000000
... NY21947000000101          001105600508416J00000000000000000000000000000000000000
... NY21947000000111          001123000508621J00000000000000000000000000000000000000
... NY21947000000121          001124000508637J00000000000000000000000000000000000000
... NY21947000000131          001138900509107N00000000000000000000000000000000000000
... NY21947000000141          001143700509281J00000000000000000000000000000000000000
... NY21947000000151          001146800509317J00000000000000000000000000000000000000
... NY21947000000161          001186100509492N00000000000000000000000000000000000000
... NY212488000000160000001800000000000000000000000000000000000000000000000000000000
... NY000089000000160000002000000000000000000190417000000000000000000000000000000000
... """.strip()

:meth:`netsgiro.parse` parses the input and returns a
:class:`netsgiro.Transmission` object:

>>> import netsgiro
>>> transmission = netsgiro.parse(data)
>>> transmission
Transmission(number='1091949', data_transmitter='00008080', data_recipient='00010200', date=datetime.date(2017, 4, 19))
>>> transmission.number
'1091949'

Each transmission can contain any number of assignments:

>>> len(transmission.assignments)
1
>>> assignment = transmission.assignments[0]
>>> assignment
Assignment(service_code=<ServiceCode.AVTALEGIRO: 21>, type=<AssignmentType.AVTALEGIRO_AGREEMENTS: 24>, number='0000002', account='99991042764', agreement_id=None, date=None)
>>> assignment.number
'0000002'

Each assignment can contain any number of transactions, in this case AvtaleGiro
agreement updates:

>>> pprint(assignment.transactions)
[Agreement(service_code=<ServiceCode.AVTALEGIRO: 21>, number=1, registration_type=<AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT: 1>, kid='000112000507155', notify=True),
 Agreement(service_code=<ServiceCode.AVTALEGIRO: 21>, number=2, registration_type=<AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT: 1>, kid='001006300507304', notify=False),
 Agreement(service_code=<ServiceCode.AVTALEGIRO: 21>, number=3, registration_type=<AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT: 1>, kid='001020200507462', notify=True),
 Agreement(service_code=<ServiceCode.AVTALEGIRO: 21>, number=4, registration_type=<AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT: 1>, kid='001026300507518', notify=True),
 Agreement(service_code=<ServiceCode.AVTALEGIRO: 21>, number=5, registration_type=<AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT: 1>, kid='001044400507783', notify=True),
 Agreement(service_code=<ServiceCode.AVTALEGIRO: 21>, number=6, registration_type=<AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT: 1>, kid='001045000507792', notify=False),
 Agreement(service_code=<ServiceCode.AVTALEGIRO: 21>, number=7, registration_type=<AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT: 1>, kid='001057800507922', notify=False),
 Agreement(service_code=<ServiceCode.AVTALEGIRO: 21>, number=8, registration_type=<AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT: 1>, kid='001060300509570', notify=True),
 Agreement(service_code=<ServiceCode.AVTALEGIRO: 21>, number=9, registration_type=<AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT: 1>, kid='001087600508176', notify=True),
 Agreement(service_code=<ServiceCode.AVTALEGIRO: 21>, number=10, registration_type=<AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT: 1>, kid='001105600508416', notify=True),
 Agreement(service_code=<ServiceCode.AVTALEGIRO: 21>, number=11, registration_type=<AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT: 1>, kid='001123000508621', notify=True),
 Agreement(service_code=<ServiceCode.AVTALEGIRO: 21>, number=12, registration_type=<AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT: 1>, kid='001124000508637', notify=True),
 Agreement(service_code=<ServiceCode.AVTALEGIRO: 21>, number=13, registration_type=<AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT: 1>, kid='001138900509107', notify=False),
 Agreement(service_code=<ServiceCode.AVTALEGIRO: 21>, number=14, registration_type=<AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT: 1>, kid='001143700509281', notify=True),
 Agreement(service_code=<ServiceCode.AVTALEGIRO: 21>, number=15, registration_type=<AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT: 1>, kid='001146800509317', notify=True),
 Agreement(service_code=<ServiceCode.AVTALEGIRO: 21>, number=16, registration_type=<AvtaleGiroRegistrationType.NEW_OR_UPDATED_AGREEMENT: 1>, kid='001186100509492', notify=False)]

As you can see, all updates here are for new or updated agreements. If a payer
deletes their AvtaleGiro agreement the ``registration_type`` field will be
:attr:`~netsgiro.AvtaleGiroRegistrationType.DELETED_AGREEMENT`.


Building payment requests
=========================

Once you have established AvtaleGiro agreements with some payers, you can start
creating payment requests based on your invoices.

You start by creating a :class:`~netsgiro.Transmission` with Nets as the
recipient:

>>> from datetime import date
>>> from decimal import Decimal
>>> import netsgiro
>>> transmission = netsgiro.Transmission(
... 	number='1703231',
...	data_transmitter='01234567',
...	data_recipient=netsgiro.NETS_ID)

Then, add an AvtaleGiro transaction assignment to the transmission using
:meth:`~netsgiro.Transmission.add_assignment`:

>>> assignment = transmission.add_assignment(
... 	service_code=netsgiro.ServiceCode.AVTALEGIRO,
...	assignment_type=netsgiro.AssignmentType.TRANSACTIONS,
...	number='0323001',
...	account='99998877777')

For each invoice, add a payment requests to the assignment using
:meth:`~netsgiro.Assignment.add_payment_request`:

>>> payment_request = assignment.add_payment_request(
...     kid='000133700501645',
...     due_date=date(2017, 4, 6),
...     amount=Decimal('5244.63'),
...     reference='ACME invoice #50164',
...     payer_name='Wonderland',
...     bank_notification=None)

Finally, you can write out the OCR data using
:meth:`~netsgiro.Transmission.to_ocr()`:

>>> data = transmission.to_ocr()
>>> print(data)
NY000010012345671703231000080800000000000000000000000000000000000000000000000000
NY210020000000000032300199998877777000000000000000000000000000000000000000000000
NY2102300000001060417           00000000000524463          000133700501645000000
NY2102310000001Wonderland                         ACME invoice #50164      00000
NY210088000000010000000400000000000524463060417060417000000000000000000000000000
NY000089000000010000000600000000000524463060417000000000000000000000000000000000

Before delivering the transmission to Nets, remember to encode it using the
ISO-8859-1 encoding to correctly preserve Norwegian letters.

To encode a bytestring with the correct encoding::

    encoded_data = data.encode('iso-8859-1')

To save the result a file with the correct encoding::

    with open('my-ocr-file.txt', 'wt', encoding='iso-8859-1') as fh:
	fh.write(data)


Building payment cancellations
==============================

To cancel one or more AvtaleGiro payment requests, the process is very similar
to creating payment requests. You start with a :class:`~netsgiro.Transmission`:

>>> from datetime import date
>>> from decimal import Decimal
>>> import netsgiro
>>> transmission = netsgiro.Transmission(
... 	number='1703232',
...	data_transmitter='01234567',
...	data_recipient=netsgiro.NETS_ID)

Add a AvtaleGiro cancellation assignment to the transmission using
:meth:`~netsgiro.Transmission.add_assignment`:

>>> assignment = transmission.add_assignment(
... 	service_code=netsgiro.ServiceCode.AVTALEGIRO,
...	assignment_type=netsgiro.AssignmentType.AVTALEGIRO_CANCELLATIONS,
...	number='0323002',
...	account='99998877777')

Add one or more payment cancellations to the assignment using
:meth:`~netsgiro.Assignment.add_payment_cancellation`:

>>> transaction = assignment.add_payment_cancellation(
...     kid='000133700501645',
...     due_date=date(2017, 4, 6),
...     amount=Decimal('5244.63'),
...     reference='ACME invoice #50164',
...     payer_name='Wonderland',
...     bank_notification=None)

The arguments passed to :meth:`~netsgiro.Assignment.add_payment_cancellation`
must be identical to the arguments passed to
:meth:`~netsgiro.Assignment.add_payment_request` when creating the payment
request you are now cancelling.

Finally, you can write out the OCR data using
:meth:`~netsgiro.Transmission.to_ocr()` and write the result to a file.

>>> data = transmission.to_ocr()
>>> print(data)
NY000010012345671703232000080800000000000000000000000000000000000000000000000000
NY213620000000000032300299998877777000000000000000000000000000000000000000000000
NY2193300000001060417           00000000000524463          000133700501645000000
NY2193310000001Wonderland                         ACME invoice #50164      00000
NY213688000000010000000400000000000524463060417060417000000000000000000000000000
NY000089000000010000000600000000000524463060417000000000000000000000000000000000


Parsing OCR Giro transactions
=============================

When receiving payments to your bank account, you'll receive OCR Giro files
with lists of all the transactions.

For the purpose of the following example we use the following input data:

>>> data = """
... NY000010000080800170031000102000000000000000000000000000000000000000000000000000
... NY090020001008566000000299991042764000000000000000000000000000000000000000000000
... NY09213000000012001921320101464000000000000102000                  0000531000000
... NY092131000000196368271940990385620000000160192999905123410000000000000000000000
... NY0921320000001Foo bar baz                             0000000000000000000000000
... NY09103000000022001921320101464000000000000102000                  0036633000000
... NY091031000000297975960160975960161883206160192999910055240000000000000000000000
... NY09103000000032001921320101464000000000000056000                  0048763000000
... NY091031000000397975816750975816751883206170192999910427640000000000000000000000
... NY09103000000042001921320101464000000000000102000                  0063851000000
... NY091031000000497975857600975857601883206170192999910055240000000000000000000000
... NY09103000000052001921320101464000000000000102000                  0120243000000
... NY091031000000597975915790975915791883206170192999905678980000000000000000000000
... NY09103000000062001921320101464000000000000056000                  0165867000000
... NY091031000000697975851090975851091883206160192999910427640000000000000000000000
... NY09103000000072001921320101464000000000000102000                  0178357000000
... NY091031000000797975848550975848551883206160192999910055240000000000000000000000
... NY09113000000082001921320101570000000000000150000           02212291038306000000
... NY091131000000896000000006001553800000000200192999995455280000000000000000000000
... NY09123000000092001921320101570000000000000120000           02311291038304000000
... NY091231000000900000000000010201690000000000000999910154060000000000000000000000
... NY09133000000102001921320101570000000000000055000           02310291038308000000
... NY091331000001000000000002206638000000000000000999910175300000000000000000000000
... NY09113000000112001921320231570000000000000194300                000149012000000
... NY091131000001196000000006001552110000000200192999905080340000000000000000000000
... NY09123000000122001921320231570000000000000100000           01211291038306000000
... NY091231000001200000000000010201690000000000000999905080340000000000000000000000
... NY09133000000132001921320231570000000000000050000           02111291038305000000
... NY091331000001300000000000320663700000000000000999905230840000000000000000000000
... NY09133000000142001921320335572000000000002050000           02321291038303000000
... NY091331000001400000000000250663700000000000000999905100550000000000000000000000
... NY09133000000152001921320941570000000000000550000           02331291038302000000
... NY091331000001500000000007974896260000000000000999910111250000000000000000000000
... NY09133000000162001921320941570000000000001050000           02341291038301000000
... NY091331000001600000000000281163700000000000000999995455280000000000000000000000
... NY09103000000172001921320941570000000000000064400           02358291038305000000
... NY091031000001700000000002806638000000000000000999995455280000000000000000000000
... NY09103000000182001921320904514000000000000056400           02311291029238000000
... NY091031000001896367780030913067140000000170192999910154060000000000000000000000
... NY09103000000192001921320904514000000000000028800           02311291034832000000
... NY091031000001996367778210976949990000000160192999910080340000000000000000000000
... NY09103000000202001921320904514000000000000054000           02311291133188000000
... NY091031000002096367781170913088610000000170192999910111250000000000000000000000
... NY090088000000200000004300000000005144900200192200192200192000000000000000000000
... NY000089000000200000004500000000005144900200192000000000000000000000000000000000
... """.strip()

:meth:`netsgiro.parse` parses the input and returns a
:class:`netsgiro.Transmission` object:

>>> import netsgiro
>>> transmission = netsgiro.parse(data)
>>> transmission
Transmission(number='0170031', data_transmitter='00008080', data_recipient='00010200', date=datetime.date(1992, 1, 20))
>>> transmission.number
'0170031'

Each transmission can contain any number of assignments:

>>> len(transmission.assignments)
1
>>> assignment = transmission.assignments[0]
>>> assignment
Assignment(service_code=<ServiceCode.OCR_GIRO: 9>, type=<AssignmentType.TRANSACTIONS: 0>, number='0000002', account='99991042764', agreement_id='001008566', date=datetime.date(1992, 1, 20))
>>> assignment.number
'0000002'
>>> assignment.get_earliest_transaction_date()
datetime.date(1992, 1, 20)
>>> assignment.get_latest_transaction_date()
datetime.date(1992, 1, 20)
>>> assignment.get_total_amount()
Decimal('51449')

Each assignment can contain any number of transactions, in this case OCR Giro
payment transactions:

>>> pprint(assignment.transactions)
[Transaction(service_code=<ServiceCode.OCR_GIRO: 9>, type=<TransactionType.PURCHASE_WITH_TEXT: 21>, number=1, date=datetime.date(1992, 1, 20), amount=Decimal('1020'), kid='0000531', reference='099038562', text='Foo bar baz', centre_id='13', day_code=20, partial_settlement_number=1, partial_settlement_serial_number='01464', sign='0', form_number='9636827194', bank_date=datetime.date(1992, 1, 16), debit_account='99990512341', _filler='0000000'),
 Transaction(service_code=<ServiceCode.OCR_GIRO: 9>, type=<TransactionType.FROM_GIRO_DEBITED_ACCOUNT: 10>, number=2, date=datetime.date(1992, 1, 20), amount=Decimal('1020'), kid='0036633', reference='097596016', text=None, centre_id='13', day_code=20, partial_settlement_number=1, partial_settlement_serial_number='01464', sign='0', form_number='9797596016', bank_date=datetime.date(1992, 1, 16), debit_account='99991005524', _filler='1883206'),
 Transaction(service_code=<ServiceCode.OCR_GIRO: 9>, type=<TransactionType.FROM_GIRO_DEBITED_ACCOUNT: 10>, number=3, date=datetime.date(1992, 1, 20), amount=Decimal('560'), kid='0048763', reference='097581675', text=None, centre_id='13', day_code=20, partial_settlement_number=1, partial_settlement_serial_number='01464', sign='0', form_number='9797581675', bank_date=datetime.date(1992, 1, 17), debit_account='99991042764', _filler='1883206'),
 Transaction(service_code=<ServiceCode.OCR_GIRO: 9>, type=<TransactionType.FROM_GIRO_DEBITED_ACCOUNT: 10>, number=4, date=datetime.date(1992, 1, 20), amount=Decimal('1020'), kid='0063851', reference='097585760', text=None, centre_id='13', day_code=20, partial_settlement_number=1, partial_settlement_serial_number='01464', sign='0', form_number='9797585760', bank_date=datetime.date(1992, 1, 17), debit_account='99991005524', _filler='1883206'),
 Transaction(service_code=<ServiceCode.OCR_GIRO: 9>, type=<TransactionType.FROM_GIRO_DEBITED_ACCOUNT: 10>, number=5, date=datetime.date(1992, 1, 20), amount=Decimal('1020'), kid='0120243', reference='097591579', text=None, centre_id='13', day_code=20, partial_settlement_number=1, partial_settlement_serial_number='01464', sign='0', form_number='9797591579', bank_date=datetime.date(1992, 1, 17), debit_account='99990567898', _filler='1883206'),
 Transaction(service_code=<ServiceCode.OCR_GIRO: 9>, type=<TransactionType.FROM_GIRO_DEBITED_ACCOUNT: 10>, number=6, date=datetime.date(1992, 1, 20), amount=Decimal('560'), kid='0165867', reference='097585109', text=None, centre_id='13', day_code=20, partial_settlement_number=1, partial_settlement_serial_number='01464', sign='0', form_number='9797585109', bank_date=datetime.date(1992, 1, 16), debit_account='99991042764', _filler='1883206'),
 Transaction(service_code=<ServiceCode.OCR_GIRO: 9>, type=<TransactionType.FROM_GIRO_DEBITED_ACCOUNT: 10>, number=7, date=datetime.date(1992, 1, 20), amount=Decimal('1020'), kid='0178357', reference='097584855', text=None, centre_id='13', day_code=20, partial_settlement_number=1, partial_settlement_serial_number='01464', sign='0', form_number='9797584855', bank_date=datetime.date(1992, 1, 16), debit_account='99991005524', _filler='1883206'),
 Transaction(service_code=<ServiceCode.OCR_GIRO: 9>, type=<TransactionType.FROM_STANDING_ORDERS: 11>, number=8, date=datetime.date(1992, 1, 20), amount=Decimal('1500'), kid='02212291038306', reference='600155380', text=None, centre_id='13', day_code=20, partial_settlement_number=1, partial_settlement_serial_number='01570', sign='0', form_number='9600000000', bank_date=datetime.date(1992, 1, 20), debit_account='99999545528', _filler='0000000'),
 Transaction(service_code=<ServiceCode.OCR_GIRO: 9>, type=<TransactionType.FROM_DIRECT_REMITTANCE: 12>, number=9, date=datetime.date(1992, 1, 20), amount=Decimal('1200'), kid='02311291038304', reference='001020169', text=None, centre_id='13', day_code=20, partial_settlement_number=1, partial_settlement_serial_number='01570', sign='0', form_number='0000000000', bank_date=None, debit_account='99991015406', _filler='0000000'),
 Transaction(service_code=<ServiceCode.OCR_GIRO: 9>, type=<TransactionType.FROM_BUSINESS_TERMINAL_GIRO: 13>, number=10, date=datetime.date(1992, 1, 20), amount=Decimal('550'), kid='02310291038308', reference='220663800', text=None, centre_id='13', day_code=20, partial_settlement_number=1, partial_settlement_serial_number='01570', sign='0', form_number='0000000000', bank_date=None, debit_account='99991017530', _filler='0000000'),
 ...
 Transaction(service_code=<ServiceCode.OCR_GIRO: 9>, type=<TransactionType.FROM_GIRO_DEBITED_ACCOUNT: 10>, number=20, date=datetime.date(1992, 1, 20), amount=Decimal('540'), kid='02311291133188', reference='091308861', text=None, centre_id='13', day_code=20, partial_settlement_number=9, partial_settlement_serial_number='04514', sign='0', form_number='9636778117', bank_date=datetime.date(1992, 1, 17), debit_account='99991011125', _filler='0000000')]
