=======
tart.py
=======

Python implementation inspired from `tart.js <https://github.com/organix/tartjs>`_.

Differences
===========

- No sponsors yet (experimenting with each actor creating its children).
- Each actor has its own event loop.

Example
=======

Run example with:

.. code-block:: bash

   python3 example.py

Press ``Ctrl-C`` to stop the event loops and exit.

Erlang Challenge
================

Create a ring of ``M`` actors, sending ``N`` messages around the ring:

.. code-block:: bash

   python3 erlang_challenge.py M N

No benchmarks yet.
