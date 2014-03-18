"""

Very basic implementation of an event loop
==========================================

The eventloop is a singleton to schedule and run events.

Exports
-------

- ``EventLoop``: the basic eventloop

"""

import queue
import sched
import threading
import time

from .singleton import Singleton


class EventLoop(object, metaclass=Singleton):
    """A generic event loop object."""

    def __init__(self):
        self.scheduler = sched.scheduler()

    def schedule(self, event):
        """Schedule an event.

        An `event` is a thunk.

        """
        self.scheduler.enter(0, 1, event)

    def stop(self):
        """Stop the loop."""
        pass
        
    def run(self, block=False):
        self.scheduler.run(blocking=block)

    def run_forever(self, wait=0.05):
        while True:
            self.run()
            time.sleep(wait)
            
    def run_in_thread(self):
        self.thread = threading.Thread(target=self.run_forever,
                                       name='event_loop')
        self.thread.daemon = True
        self.thread.start()
        
