=========
Changelog
=========


v1.1.0 (2017-10-23)
===================

Record parsing and writing are now tested with an additional suite of property
based tests, using the Hypothesis library. This testing effort identified a
number of issues, all of which are fixed by this release.

- Fixed exception in :meth:`netsgiro.records.TransactionAmountItem2.to_ocr()`
  if :attr:`~netsgiro.records.TransactionAmountItem2.payer_name` was
  :class:`None`.

- Fixed exception in :meth:`netsgiro.records.TransactionAmountItem3.to_ocr()`
  if :attr:`~netsgiro.records.TransactionAmountItem3.text` was
  :class:`None`.

- Raise a :exc:`ValueError` if a too long string is used for any of:

  - :attr:`netsgiro.records.TransactionAmountItem1.kid` (max 25 chars)
  - :attr:`netsgiro.records.TransactionAmountItem3.text` (max 40 chars)
  - :attr:`netsgiro.records.TransactionSpecification.text` (max 40 chars)
  - :attr:`netsgiro.records.AvtaleGiroAgreement.kid` (max 25 chars)

  Previously the string was accepted and the record generated invalid OCR data.

- Strip newline characters (``\n`` and ``\r``) from record strings, like
  :attr:`netsgiro.records.TransactionAmountItem2.payer_name`.

  Previously the newline characters were accepted and the record generated
  invalid OCR data.

- Automatically pad :attr:`netsgiro.records.TransactionSpecification.text` to
  40 chars, so that a manually created record and a record parsed from OCR are
  identical.


v1.0.0 (2017-05-20)
===================

No changes from v1.0.0a3, which has been used in production for a few weeks
without any issues.


v1.0.0a3 (2017-05-03)
=====================

- Rename :attr:`netsgiro.TransactionType.AVTALEGIRO_AGREEMENTS` (plural)
  to :attr:`netsgiro.TransactionType.AVTALEGIRO_AGREEMENT` (singular).

- When writing record to OCR, cut
  :attr:`netsgiro.records.TransactionAmountItem2.payer_name` to 10 first chars,
  as that is all the field has room for.


v1.0.0a2 (2017-04-26)
=====================

Major improvements and changes.

- The objects API now supports parsing all known file variants with
  :meth:`netsgiro.parse` and can recreate the parsed OCR data perfectly with
  :meth:`netsgiro.Transmission.to_ocr`.

- The objects API now does all the bookkeeping necessary for building payment
  requests. With this improvement, the code necessary to produce a payment
  request is cut to from around 100 to 25 lines of code.

- New :doc:`quickstart guide <quickstart>` shows how to parse files and build
  payment requests.

- All public methods and fields of both the
  :doc:`objects API <objects>` and :doc:`records API <records>` are now
  documented.

- The low-level :doc:`records API <records>` has been moved to the
  :mod:`netsgiro.records` module.


v1.0.0a1 (2017-04-17)
=====================

Initial alpha release. No promises about backwards compatibility.
