========
netsgiro
========

File parsers for Nets AvtaleGiro and OCR Giro.


File format examples
====================

The following is an example of an AvtaleGiro payment request file::

    >>> data = open('tests/data/avtalegiro_payment_request.txt').read()
    >>> print(data)
    NY000010555555551000081000080800000000000000000000000000000000000000000000000000
    NY210020000000000400008688888888888000000000000000000000000000000000000000000000
    NY2121300000001170604           00000000000000100          008000011688373000000
    NY2121310000001NAVN                                                        00000
    NY212149000000140011 Gjelder Faktura: 168837  Dato: 19/03/0400000000000000000000
    NY212149000000140012                  ForfallsDato: 17/06/0400000000000000000000
    NY2121300000002170604           00000000000000100          008000021688389000000
    NY2121310000002NAVN                                                        00000
    NY212149000000240011 Gjelder Faktura: 168838  Dato: 19/03/0400000000000000000000
    NY212149000000240012                  ForfallsDato: 17/06/0400000000000000000000
    NY2121300000003170604           00000000000000100          008000031688395000000
    NY2121310000003NAVN                                                        00000
    NY2121300000004170604           00000000000000100          008000041688401000000
    NY2121310000004NAVN                                                        00000
    NY2121300000005170604           00000000000000100          008000051688416000000
    NY2121310000005NAVN                                                        00000
    NY212149000000540011 Gjelder Faktura: 168841  Dato: 19/03/0400000000000000000000
    NY212149000000540012                  ForfallsDato: 17/06/0400000000000000000000
    NY2102300000006170604           00000000000000100          008000061688422000000
    NY2102310000006NAVN                                                        00000
    NY210088000000060000002000000000000000600170604170604000000000000000000000000000
    NY000089000000060000002200000000000000600170604000000000000000000000000000000000

The same file is used in the API examples below.


Low level API
=============

netsgiro's low level API parses OCR files into a list of records::

    >>> import netsgiro
    >>> netsgiro.get_records(data)
    [TransmissionStart(service_code=<ServiceCode.NONE: 0>, record_type=<RecordType.TRANSMISSION_START: 10>, transmission_type=0, data_transmitter='55555555', transmission_number='1000081', data_recipient='00008080'),
    AssignmentStart(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.ASSIGNMENT_START: 20>, assignment_type=<AssignmentType.TRANSACTIONS: 0>, agreement_id='000000000', assignment_number='4000086', assignment_account='88888888888'),
    AvtaleGiroAmountItem1(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.TRANSACTION_AMOUNT_1: 30>, transaction_type=<TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>, transaction_number='0000001', nets_date=datetime.date(2004, 6, 17), amount=100, kid='008000011688373'),
    AvtaleGiroAmountItem2(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.TRANSACTION_AMOUNT_2: 31>, transaction_type=<TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>, transaction_number='0000001', payer_name='NAVN', reference=None),
    AvtaleGiroSpecification(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.TRANSACTION_SPECIFICATION: 49>, transaction_type=<TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>, transaction_number='0000001', line_number=1, column_number=1, text=' Gjelder Faktura: 168837  Dato: 19/03/04'),
    AvtaleGiroSpecification(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.TRANSACTION_SPECIFICATION: 49>, transaction_type=<TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>, transaction_number='0000001', line_number=1, column_number=2, text='                  ForfallsDato: 17/06/04'),
    AvtaleGiroAmountItem1(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.TRANSACTION_AMOUNT_1: 30>, transaction_type=<TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>, transaction_number='0000002', nets_date=datetime.date(2004, 6, 17), amount=100, kid='008000021688389'),
    AvtaleGiroAmountItem2(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.TRANSACTION_AMOUNT_2: 31>, transaction_type=<TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>, transaction_number='0000002', payer_name='NAVN', reference=None),
    AvtaleGiroSpecification(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.TRANSACTION_SPECIFICATION: 49>, transaction_type=<TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>, transaction_number='0000002', line_number=1, column_number=1, text=' Gjelder Faktura: 168838  Dato: 19/03/04'),
    AvtaleGiroSpecification(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.TRANSACTION_SPECIFICATION: 49>, transaction_type=<TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>, transaction_number='0000002', line_number=1, column_number=2, text='                  ForfallsDato: 17/06/04'),
    AvtaleGiroAmountItem1(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.TRANSACTION_AMOUNT_1: 30>, transaction_type=<TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>, transaction_number='0000003', nets_date=datetime.date(2004, 6, 17), amount=100, kid='008000031688395'),
    AvtaleGiroAmountItem2(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.TRANSACTION_AMOUNT_2: 31>, transaction_type=<TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>, transaction_number='0000003', payer_name='NAVN', reference=None),
    AvtaleGiroAmountItem1(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.TRANSACTION_AMOUNT_1: 30>, transaction_type=<TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>, transaction_number='0000004', nets_date=datetime.date(2004, 6, 17), amount=100, kid='008000041688401'),
    AvtaleGiroAmountItem2(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.TRANSACTION_AMOUNT_2: 31>, transaction_type=<TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>, transaction_number='0000004', payer_name='NAVN', reference=None),
    AvtaleGiroAmountItem1(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.TRANSACTION_AMOUNT_1: 30>, transaction_type=<TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>, transaction_number='0000005', nets_date=datetime.date(2004, 6, 17), amount=100, kid='008000051688416'),
    AvtaleGiroAmountItem2(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.TRANSACTION_AMOUNT_2: 31>, transaction_type=<TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>, transaction_number='0000005', payer_name='NAVN', reference=None),
    AvtaleGiroSpecification(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.TRANSACTION_SPECIFICATION: 49>, transaction_type=<TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>, transaction_number='0000005', line_number=1, column_number=1, text=' Gjelder Faktura: 168841  Dato: 19/03/04'),
    AvtaleGiroSpecification(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.TRANSACTION_SPECIFICATION: 49>, transaction_type=<TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>, transaction_number='0000005', line_number=1, column_number=2, text='                  ForfallsDato: 17/06/04'),
    AvtaleGiroAmountItem1(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.TRANSACTION_AMOUNT_1: 30>, transaction_type=<TransactionType.NO_AVTALEGIRO_NOTIFICATION_FROM_BANK: 2>, transaction_number='0000006', nets_date=datetime.date(2004, 6, 17), amount=100, kid='008000061688422'),
    AvtaleGiroAmountItem2(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.TRANSACTION_AMOUNT_2: 31>, transaction_type=<TransactionType.NO_AVTALEGIRO_NOTIFICATION_FROM_BANK: 2>, transaction_number='0000006', payer_name='NAVN', reference=None),
    AssignmentEnd(service_code=<ServiceCode.AVTALEGIRO: 21>, record_type=<RecordType.ASSIGNMENT_END: 88>, assignment_type=<AssignmentType.TRANSACTIONS: 0>, num_transactions=6, num_records=20, total_amount=600, nets_date=datetime.date(2004, 6, 17), nets_date_earliest=datetime.date(2004, 6, 17), nets_date_latest=None),
    TransmissionEnd(service_code=<ServiceCode.NONE: 0>, record_type=<RecordType.TRANSMISSION_END: 89>, transmission_type=0, num_transactions=6, num_records=22, total_amount=600, nets_date=datetime.date(2004, 6, 17))]


High level API
==============

netsgiro's high level API parses OCR files into a tree of objects::

    >>> import netsgiro
    >>> transmission = netsgiro.parse(data)
    >>> transmission.to_dict()
    {'assignments': [{'account': '88888888888',
       'agreement_id': '000000000',
       'number': '4000086',
       'service_code': <ServiceCode.AVTALEGIRO: 21>,
       'transactions': [{'amount': Decimal('1'),
         'nets_date': datetime.date(2004, 6, 17),
         'kid': '008000011688373',
         'number': '0000001',
         'payer_name': 'NAVN',
         'reference': None,
         'service_code': <ServiceCode.AVTALEGIRO: 21>,
         'specification_text': ' Gjelder Faktura: 168837  Dato: 19/03/04                  ForfallsDato: 17/06/04\n',
         'type': <TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>},
        {'amount': Decimal('1'),
         'nets_date': datetime.date(2004, 6, 17),
         'kid': '008000021688389',
         'number': '0000002',
         'payer_name': 'NAVN',
         'reference': None,
         'service_code': <ServiceCode.AVTALEGIRO: 21>,
         'specification_text': ' Gjelder Faktura: 168838  Dato: 19/03/04                  ForfallsDato: 17/06/04\n',
         'type': <TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>},
        {'amount': Decimal('1'),
         'nets_date': datetime.date(2004, 6, 17),
         'kid': '008000031688395',
         'number': '0000003',
         'payer_name': 'NAVN',
         'reference': None,
         'service_code': <ServiceCode.AVTALEGIRO: 21>,
         'specification_text': '',
         'type': <TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>},
        {'amount': Decimal('1'),
         'nets_date': datetime.date(2004, 6, 17),
         'kid': '008000041688401',
         'number': '0000004',
         'payer_name': 'NAVN',
         'reference': None,
         'service_code': <ServiceCode.AVTALEGIRO: 21>,
         'specification_text': '',
         'type': <TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>},
        {'amount': Decimal('1'),
         'nets_date': datetime.date(2004, 6, 17),
         'kid': '008000051688416',
         'number': '0000005',
         'payer_name': 'NAVN',
         'reference': None,
         'service_code': <ServiceCode.AVTALEGIRO: 21>,
         'specification_text': ' Gjelder Faktura: 168841  Dato: 19/03/04                  ForfallsDato: 17/06/04\n',
         'type': <TransactionType.AVTALEGIRO_NOTIFICATION_FROM_BANK: 21>},
        {'amount': Decimal('1'),
         'nets_date': datetime.date(2004, 6, 17),
         'kid': '008000061688422',
         'number': '0000006',
         'payer_name': 'NAVN',
         'reference': None,
         'service_code': <ServiceCode.AVTALEGIRO: 21>,
         'specification_text': '',
         'type': <TransactionType.AVTALEGIRO_NO_NOTIFICATION_FROM_BANK: 2>}]}],
     'data_recipient': '00008080',
     'data_transmitter': '55555555',
     'nets_date': datetime.date(2004, 6, 17),
     'number': '1000081'}


License
=======

Copyright 2017 Otovo AS.

Licensed under the Apache License, Version 2.0. See the ``LICENSE`` file.


Project resources
=================

- `Source code <https://github.com/otovo/python-netsgiro>`_
- `Issue tracker <https://github.com/otovo/python-netsgiro/issues>`_

.. image:: https://img.shields.io/pypi/v/netsgiro.svg?style=flat
    :target: https://pypi.org/project/netsgiro/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/travis/otovo/python-netsgiro/master.svg?style=flat
    :target: https://travis-ci.org/otovo/python-netsgiro
    :alt: Travis CI build status
