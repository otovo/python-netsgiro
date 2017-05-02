=========
Changelog
=========


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
