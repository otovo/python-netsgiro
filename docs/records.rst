===========
Records API
===========

The records API is the lowest level API. It parses each line of "OCR" text
input into a record object. A record object also knows about its OCR
representation.

.. autofunction:: netsgiro.get_records


Record types
============

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
