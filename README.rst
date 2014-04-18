=======
tart.py
=======

Python implementation of the `Actor Model`_ inspired from `tart.js`_.

Overview
========

The initial ideas for ``tartpy`` are copied from `@dalnefre`_ and
`@tristanls`_.  At the beginning, the goal was to replicate `tart.js`_
in Python.  Lately, it has diverged slightly, to experiment with the
new Python asynchrony model introduced in version 3.4.

``tartpy`` aims to be an actor library with the following features:

- it implements the pure actor model (rather than the Erlang model),

- it can be used in practical situations to express lock-free and
  concurrent algorithms,

- it abstracts the network transport to allow arbitrary protocols,

- it implements a `capability based approach`_ to isolate actors,
  using membranes (again, the ideas are due to `@dalnefre`_ and
  `@tristanls`_).  The semantics of membranes may differ between
  ``tartpy`` and ``tartjs``.

Installing
==========

Install with::

    $ pip install git+https://github.com/waltermoreira/tartpy

or clone this repository and install with ``python3 setup.py install``::

    $ git clone https://github.com/waltermoreira/tartpy
    $ cd tartpy
    $ python3 setup.py install

Test
====

Run tests with::

    $ python3 setup.py test


Examples
========

Run example with:

.. code-block:: bash

   python3 tartpy/example.py

There is also an `IPython notebook`_ showing the basic properties of actors.

The project `actor_model`_ contains slides and IPython notebooks from
a talk presented at TACC_ in April 17, 2014.


Erlang Challenge
================

Create a ring of ``M`` actors, sending ``N`` messages around the ring:

.. code-block:: bash

   python3 tartpy/erlang_challenge.py M N

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

.. _Actor Model: http://en.wikipedia.org/wiki/Actor_model
.. _tart.js: https://github.com/organix/tartjs
.. _@dalnefre: https://github.com/dalnefre
.. _@tristanls: https://github.com/tristanls
.. _capability based approach: http://en.wikipedia.org/wiki/Capability-based_security
.. _IPython notebook: http://nbviewer.ipython.org/github/waltermoreira/tartpy/blob/master/demo/tartpy_demo.ipynb
.. _actor_model: https://github.com/waltermoreira/actor_model
.. _TACC: https://www.tacc.utexas.edu/
