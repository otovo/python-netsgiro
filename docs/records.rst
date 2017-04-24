===========
Records API
===========

The records API is the lower level API. It parses each line of "OCR" text
input into a record object. A record object also knows about its OCR
representation.


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

:meth:`netsgiro.get_records` parses the input and returns a record object for
each line of input:

>>> records = netsgiro.get_records(data)
>>> len(records)
22
>>> pprint(records)
[TransmissionStart(service_code=<ServiceCode.NONE: 0>, transmission_number='1000081', data_transmitter='55555555', data_recipient='00008080', record_type=<RecordType.TRANSMISSION_START: 10>),
 AssignmentStart(service_code=<ServiceCode.AVTALEGIRO: 21>, assignment_type=<AssignmentType.TRANSACTIONS: 0>, assignment_number='4000086', assignment_account='88888888888', agreement_id='000000000', record_type=<RecordType.ASSIGNMENT_START: 20>),
 TransactionAmountItem1(service_code=<ServiceCode.AVTALEGIRO: 21>, transaction_type=<TransactionType.PURCHASE_WITH_TEXT: 21>, transaction_number=1, nets_date=datetime.date(2004, 6, 17), amount=100, kid='008000011688373', centre_id=None, day_code=None, partial_settlement_number=None, partial_settlement_serial_number=None, sign=None, record_type=<RecordType.TRANSACTION_AMOUNT_ITEM_1: 30>),
 TransactionAmountItem2(service_code=<ServiceCode.AVTALEGIRO: 21>, transaction_type=<TransactionType.PURCHASE_WITH_TEXT: 21>, transaction_number=1, reference=None, form_number=None, bank_date=None, debit_account=None, _filler=None, payer_name='NAVN', record_type=<RecordType.TRANSACTION_AMOUNT_ITEM_2: 31>),
 TransactionSpecification(service_code=<ServiceCode.AVTALEGIRO: 21>, transaction_type=<TransactionType.PURCHASE_WITH_TEXT: 21>, transaction_number=1, line_number=1, column_number=1, text=' Gjelder Faktura: 168837  Dato: 19/03/04', record_type=<RecordType.TRANSACTION_SPECIFICATION: 49>),
 TransactionSpecification(service_code=<ServiceCode.AVTALEGIRO: 21>, transaction_type=<TransactionType.PURCHASE_WITH_TEXT: 21>, transaction_number=1, line_number=1, column_number=2, text='                  ForfallsDato: 17/06/04', record_type=<RecordType.TRANSACTION_SPECIFICATION: 49>),
 ...
 AssignmentEnd(service_code=<ServiceCode.AVTALEGIRO: 21>, assignment_type=<AssignmentType.TRANSACTIONS: 0>, num_transactions=6, num_records=20, total_amount=600, nets_date_1=datetime.date(2004, 6, 17), nets_date_2=datetime.date(2004, 6, 17), nets_date_3=None, record_type=<RecordType.ASSIGNMENT_END: 88>),
 TransmissionEnd(service_code=<ServiceCode.NONE: 0>, num_transactions=6, num_records=22, total_amount=600, nets_date=datetime.date(2004, 6, 17), record_type=<RecordType.TRANSMISSION_END: 89>)]


.. autofunction:: netsgiro.get_records


Record types
============

Given a record object, all record fields are available as sensible Python
types:

>>> assignment_end = records[-2]
>>> assignment_end.service_code
<ServiceCode.AVTALEGIRO: 21>
>>> assignment_end.assignment_type
<AssignmentType.TRANSACTIONS: 0>
>>> assignment_end.nets_date_earliest
datetime.date(2004, 6, 17)
>>> assignment_end.nets_date_latest
datetime.date(2004, 6, 17)
>>> assignment_end.num_records
20
>>> assignment_end.num_transactions
6
>>> assignment_end.total_amount
600

You can also convert the record back to an OCR string:

>>> assignment_end.to_ocr()
'NY210088000000060000002000000000000000600170604170604000000000000000000000000000'

For details on the semantics of each field, please refer to Nets'
documentations. The :file:`reference` directory of the netsgiro Git repo
contains the file format specifications, which is a good place to start.


.. autoclass:: netsgiro.TransmissionStart
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: netsgiro.TransmissionEnd
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: netsgiro.AssignmentStart
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: netsgiro.AssignmentEnd
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: netsgiro.TransactionAmountItem1
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: netsgiro.TransactionAmountItem2
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: netsgiro.TransactionAmountItem3
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: netsgiro.TransactionSpecification
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: netsgiro.AvtaleGiroAgreement
   :members:
   :undoc-members:
   :inherited-members:
