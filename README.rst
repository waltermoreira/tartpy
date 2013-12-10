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

Benchmarks
----------

For ``M = 100000`` and ``N = 10``::

    Starting 100000 actor ring
    Construction time: 1.5192079544067383 seconds
    Loop times:
      0.7743091583251953 seconds
      0.7793149948120117 seconds
      0.7702958583831787 seconds
      0.7602570056915283 seconds
      0.7704610824584961 seconds
      0.779731035232544 seconds
      0.7654228210449219 seconds
      0.7625432014465332 seconds
      0.7740719318389893 seconds
      0.7699680328369141 seconds
    Average: 0.7706375122070312 seconds

