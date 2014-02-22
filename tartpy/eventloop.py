"""

Very basic implementation of an event loop
==========================================

Exports
-------

- ``ThreadedEventLoop``: global event loop running in a thread

- ``ManualEventLoop``: global event loop to be run synchronously

- ``individual_loop_step``: process one event

- ``individual_loop``: process events indefinitely

"""

import queue
import sys
import threading
import time
import traceback

from .singleton import Singleton


def _format_exception(exc_info):
    """Create a message with details on the exception."""
    exc_type, exc_value, exc_tb = exc_info
    return {'exception': {'type': exc_type,
                          'value': exc_value,
                          'traceback': exc_tb},
            'traceback': traceback.format_exception(*exc_info)}
    

class EventLoop(object, metaclass=Singleton):
    """A generic event loop object."""

    def __init__(self):
        self.queue = queue.Queue()

    def schedule(self, event):
        """Schedule an event."""
        self.queue.put(event)

    def stop(self):
        """Stop the loop."""
        pass
        
    def run_step(self, block=True):
        ev, error = self.queue.get(block=block)
        try:
            ev()
        except Exception as exc:
            error(_format_exception(sys.exc_info()))

    def run(self):
        try:
            while True:
                self.run_step(block=False)
        except queue.Empty:
            return
            

