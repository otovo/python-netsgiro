========
netsgiro
========

netsgiro is a Python library for working with `Nets <https://www.nets.eu/>`_
AvtaleGiro and OCR Giro files.

AvtaleGiro is a direct debit solution that is in widespread use in Norway, with
more than 15 000 companies offering to their customers. OCR Giro files are used
by Nets and Norwegian banks to update payees on recent payments done to their
accounts.  In combination, AvtaleGiro and OCR Giro allows for a high level of
automation of invoicing and payment processing.

The netsgiro library supports:

- Parsing OCR Giro transactions
- Parsing AvtaleGiro agreements
- Creating AvtaleGiro payment requests
- Creating AvtaleGiro cancellations

For details and code examples, see `the netsgiro documentation
<https://netsgiro.readthedocs.io/>`_.

For details on the file formats and their semantics, please refer to the
official `AvtaleGiro <https://www.avtalegiro.no/>`_ and
`OCR Giro <https://www.nets.eu/no-nb/losninger/inn-og-utbetalinger/ocrgiro/Pages/default.aspx>`_
documentation from Nets.


License
=======

Copyright 2017 Otovo AS.

Licensed under the Apache License, Version 2.0. See the ``LICENSE`` file.


Project resources
=================

- `Documentation <https://netsgiro.readthedocs.io/>`_
- `Source code <https://github.com/otovo/python-netsgiro>`_
- `Issue tracker <https://github.com/otovo/python-netsgiro/issues>`_

.. image:: https://img.shields.io/pypi/v/netsgiro.svg?style=flat
    :target: https://pypi.org/project/netsgiro/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/travis/otovo/python-netsgiro/master.svg?style=flat
    :target: https://travis-ci.org/otovo/python-netsgiro
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/otovo/python-netsgiro/master.svg?style=flat
    :target: https://coveralls.io/github/otovo/python-netsgiro
    :alt: Test coverage
