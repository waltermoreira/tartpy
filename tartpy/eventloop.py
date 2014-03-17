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

        An `event` is a thunk.

        """
        self.queue.put(event)

    def stop(self):
        """Stop the loop."""
        pass
        
    def run_step(self, block=True):
        """Process one event."""
        ev = self.queue.get(block=block)
        ev()

    def run(self, block=False):
        """Process all events in the queue."""
        try:
            while True:
                self.run_step(block=block)
        except queue.Empty:
            return
            
    def run_in_thread(self):
        self.thread = threading.Thread(target=self.run, args=(True,),
                                       name='event_loop')
        self.thread.daemon = True
        self.thread.start()
        
