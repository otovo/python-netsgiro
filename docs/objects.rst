===========
Objects API
===========

The object API is the higher level API. It parses the "OCR" file into an object
structure that for most use cases is more pleasant to work with than the lower
level :doc:`records API <records>`.


File parsing
============

To parse an OCR file, you must first read the contents of the OCR file. It
should be decoded using the ISO-8559-1 encoding::

    with open('my-ocr-file.txt', 'r', encoding='iso-8859-1') as fh:
        data = fh.read()

For the purpose of the following example we use the following input data:

>>> data = '''
... NY000010555555551000081000080800000000000000000000000000000000000000000000000000
... NY210020000000000400008688888888888000000000000000000000000000000000000000000000
... NY2121300000001170604           00000000000000100          008000011688373000000
... NY2121310000001NAVN                                                        00000
... NY212149000000140011 Gjelder Faktura: 168837  Dato: 19/03/0400000000000000000000
... NY212149000000140012                  ForfallsDato: 17/06/0400000000000000000000
... NY2121300000002170604           00000000000000100          008000021688389000000
... NY2121310000002NAVN                                                        00000
... NY212149000000240011 Gjelder Faktura: 168838  Dato: 19/03/0400000000000000000000
... NY212149000000240012                  ForfallsDato: 17/06/0400000000000000000000
... NY2121300000003170604           00000000000000100          008000031688395000000
... NY2121310000003NAVN                                                        00000
... NY2121300000004170604           00000000000000100          008000041688401000000
... NY2121310000004NAVN                                                        00000
... NY2121300000005170604           00000000000000100          008000051688416000000
... NY2121310000005NAVN                                                        00000
... NY212149000000540011 Gjelder Faktura: 168841  Dato: 19/03/0400000000000000000000
... NY212149000000540012                  ForfallsDato: 17/06/0400000000000000000000
... NY2102300000006170604           00000000000000100          008000061688422000000
... NY2102310000006NAVN                                                        00000
... NY210088000000060000002000000000000000600170604170604000000000000000000000000000
... NY000089000000060000002200000000000000600170604000000000000000000000000000000000
... '''.strip()  # noqa

:meth:`netsgiro.parse` parses the input and returns a
:class:`netsgiro.Transmission` object:

>>> transmission = netsgiro.parse(data)
>>> transmission
Transmission(number='1000081', data_transmitter='55555555', data_recipient='00008080', nets_date=datetime.date(2004, 6, 17))
>>> transmission.number
'1000081'

Each transmission can contain any number of assignments:

>>> len(transmission.assignments)
1
>>> assignment = transmission.assignments[0]
>>> assignment
Assignment(service_code=<ServiceCode.AVTALEGIRO: 21>, type=<AssignmentType.TRANSACTIONS: 0>, agreement_id='000000000', number='4000086', account='88888888888', nets_date=None)
>>> assignment.number
'4000086'
>>> assignment.get_nets_date_earliest()
datetime.date(2004, 6, 17)
>>> assignment.get_nets_date_latest()
datetime.date(2004, 6, 17)
>>> assignment.get_total_amount()
Decimal('6')

Each assignment can contain any number of transactions:

>>> pprint(assignment.transactions)
[Transaction(service_code=<ServiceCode.AVTALEGIRO: 21>, type=<TransactionType.PURCHASE_WITH_TEXT: 21>, number=1, nets_date=datetime.date(2004, 6, 17), amount=Decimal('1'), kid='008000011688373', reference=None, text=' Gjelder Faktura: 168837  Dato: 19/03/04                  ForfallsDato: 17/06/04\n', centre_id=None, day_code=None, partial_settlement_number=None, partial_settlement_serial_number=None, sign=None, form_number=None, bank_date=None, debit_account=None, _filler=None, payer_name='NAVN'),
 Transaction(service_code=<ServiceCode.AVTALEGIRO: 21>, type=<TransactionType.PURCHASE_WITH_TEXT: 21>, number=2, nets_date=datetime.date(2004, 6, 17), amount=Decimal('1'), kid='008000021688389', reference=None, text=' Gjelder Faktura: 168838  Dato: 19/03/04                  ForfallsDato: 17/06/04\n', centre_id=None, day_code=None, partial_settlement_number=None, partial_settlement_serial_number=None, sign=None, form_number=None, bank_date=None, debit_account=None, _filler=None, payer_name='NAVN'),
 Transaction(service_code=<ServiceCode.AVTALEGIRO: 21>, type=<TransactionType.PURCHASE_WITH_TEXT: 21>, number=3, nets_date=datetime.date(2004, 6, 17), amount=Decimal('1'), kid='008000031688395', reference=None, text='', centre_id=None, day_code=None, partial_settlement_number=None, partial_settlement_serial_number=None, sign=None, form_number=None, bank_date=None, debit_account=None, _filler=None, payer_name='NAVN'),
 Transaction(service_code=<ServiceCode.AVTALEGIRO: 21>, type=<TransactionType.PURCHASE_WITH_TEXT: 21>, number=4, nets_date=datetime.date(2004, 6, 17), amount=Decimal('1'), kid='008000041688401', reference=None, text='', centre_id=None, day_code=None, partial_settlement_number=None, partial_settlement_serial_number=None, sign=None, form_number=None, bank_date=None, debit_account=None, _filler=None, payer_name='NAVN'),
 Transaction(service_code=<ServiceCode.AVTALEGIRO: 21>, type=<TransactionType.PURCHASE_WITH_TEXT: 21>, number=5, nets_date=datetime.date(2004, 6, 17), amount=Decimal('1'), kid='008000051688416', reference=None, text=' Gjelder Faktura: 168841  Dato: 19/03/04                  ForfallsDato: 17/06/04\n', centre_id=None, day_code=None, partial_settlement_number=None, partial_settlement_serial_number=None, sign=None, form_number=None, bank_date=None, debit_account=None, _filler=None, payer_name='NAVN'),
 Transaction(service_code=<ServiceCode.AVTALEGIRO: 21>, type=<TransactionType.AVTALEGIRO_WITH_PAYEE_NOTIFICATION: 2>, number=6, nets_date=datetime.date(2004, 6, 17), amount=Decimal('1'), kid='008000061688422', reference=None, text='', centre_id=None, day_code=None, partial_settlement_number=None, partial_settlement_serial_number=None, sign=None, form_number=None, bank_date=None, debit_account=None, _filler=None, payer_name='NAVN')]


Payment request
===============

To build an AvtaleGiro payment request, you start with a
:class:`~netsgiro.Transmission`:

>>> from datetime import date
>>> from decimal import Decimal
>>> transmission = netsgiro.Transmission(
... 	number='1703231',
...	data_transmitter='01234567',
...	data_recipient=netsgiro.NETS_ID)

Add a AvtaleGiro transaction assignment to the transmission using
:meth:`~netsgiro.Transmission.add_assignment`:

>>> assignment = transmission.add_assignment(
... 	service_code=netsgiro.ServiceCode.AVTALEGIRO,
...	assignment_type=netsgiro.AssignmentType.TRANSACTIONS,
...	number='0323001',
...	account='99998877777')

Add one or more payment requests to the assignment using
:meth:`~netsgiro.Assignment.add_payment_request`:

>>> transaction = assignment.add_payment_request(
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

Before saving it to a file or transmitting it over the network, remember to
encode it using the ISO-8859-1 encoding to correctly preserve Norwegian
letters::

    with open('my-ocr-file.txt', 'wt', encoding='iso-8859-1') as fh:
	fh.write(data)


Payment cancellation
====================

To cancel one or more AvtaleGiro payment requests, the process is very similar
to creating payment requests. You start with a :class:`~netsgiro.Transmission`:

>>> from datetime import date
>>> from decimal import Decimal
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


Transmission
============

.. autoclass:: netsgiro.Transmission
   :members:
   :undoc-members:
   :inherited-members:



Assignment
==========

.. autoclass:: netsgiro.Assignment
   :members:
   :undoc-members:
   :inherited-members:


Transaction
===========

.. autoclass:: netsgiro.Transaction
   :members:
   :undoc-members:
   :inherited-members:
