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


def actor_map(f, message):
    """Map a function f:{Actor} -> B to a message."""

    if isinstance(message, Actor):
        return f(message)
    if isinstance(message, Mapping):
        return {actor_map(f, key): actor_map(f, value)
                for key, value in message.items()}
    if isinstance(message, str):
        return message
    if isinstance(message, Sequence):
        return [actor_map(f, value) for value in message]
    return message
    