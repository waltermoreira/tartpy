from collections.abc import Mapping, Sequence
import time

from .runtime import behavior, Actor, exception_message, Runtime
from .eventloop import EventLoop


class Wait(object):
    """A synchronizing object.

    Convenience object to wait for results outside actors.

    Use as::

        w = Wait()
        wait = runtime.create(w.wait_beh)
        # now use `wait` as a customer
        msg = w.join()

    `msg` will be the message sent back to the customer.

    """

    POLL_TIME = 0.01 # seconds
    
    def __init__(self):
        self.state = None

    @behavior
    def wait_beh(self, this, message):
        self.state = message

    def join(self):
        while self.state is None:
            time.sleep(self.POLL_TIME)
        return self.state


def later(actor, t, msg):
    EventLoop().later(t, lambda: actor << msg)


@behavior
def log_beh(self, message):
    print('LOG:', message)


def dict_map(f, primitive, dic):
    """Map a function f:{primitive} -> B to a dictionary."""

    if primitive(dic):
        return f(dic)
    if isinstance(dic, Mapping):
        return {dict_map(f, primitive, key): dict_map(f, primitive, value)
                for key, value in dic.items()}
    if isinstance(dic, str):
        return dic
    if isinstance(dic, Sequence):
        return [dict_map(f, primitive, value) for value in dic]
    return dic


def actor_map(f, message):
    def primitive(x):
        return isinstance(x, Actor)
    return dict_map(f, primitive, message)
