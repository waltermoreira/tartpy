Differences with `tartjs` demo
==============================

- `Runtime` in `tartpy` is the equivalent of `sponsor` in `tartjs`.

- Behaviors in `tartpy` need the extra argument `self` which is not
  necessary in `tartjs`, since Javascript implicitly passes the
  reference `this` to the current object. (From the Zen of Python:
  "explicit is better than implicit".)

- Arguments in behaviors that are supposed to be mutated must be
  mutable objects (such as dictionaries, for example). This is due to
  the differences between closures are handled in Python and
  Javascript. (`nonlocal` new Python keyword doesn't help here for the
  general case.)

- Sending message `m` to an actor `a` can use any of these equivalent
  expression::

      a << m
      a(m)
      a.send(m)

- Membranes in `tartpy` have a different structure than in `tartjs`,
  so the example for sending messages between memory domains are
  considerably different.
