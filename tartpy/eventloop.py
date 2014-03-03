"""

Very basic implementation of an event loop
==========================================

The eventloop is a singleton to schedule and run events.

Exports
-------

- ``EventLoop``: the basic eventloop

"""

import queue
import sys
import threading
import time
import traceback

from .singleton import Singleton


def exception_message():
    """Create a message with details on the exception."""
    exc_type, exc_value, exc_tb = exc_info = sys.exc_info()
    return {'exception': {'type': exc_type,
                          'value': exc_value,
                          'traceback': exc_tb},
            'traceback': traceback.format_exception(*exc_info)}
    

class EventLoop(object, metaclass=Singleton):
    """A generic event loop object."""

    def __init__(self):
        self.queue = queue.Queue()

    def schedule(self, event):
        """Schedule an event.

        The events have the form::

            (event, error)

        where `event` is a thunk and `error` is called with an
        exception message (output of `exception_message`) if there is
        an error when executing `event`.

        """
        self.queue.put(event)

    def stop(self):
        """Stop the loop."""
        pass
        
    def run_step(self, block=True):
        """Process one event."""
        ev, error = self.queue.get(block=block)
        try:
            ev()
        except Exception as exc:
            error(exception_message())

    def run(self):
        """Process all events in the queue."""
        try:
            while True:
                self.run_step(block=False)
        except queue.Empty:
            return
            

