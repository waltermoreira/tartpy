"""

Very basic implementation of an event loop
==========================================

The eventloop is a singleton to schedule and run events.

Exports
-------

- ``EventLoop``: the basic eventloop

"""

import hashlib
import queue
import sched
import threading
import time

from .singleton import Singleton


class EventLoop(object, metaclass=Singleton):
    """A generic event loop object."""

    def __init__(self, num_workers=10):
        self.num_workers = num_workers
        self.schedulers = [sched.scheduler() for _ in range(num_workers)]

    def actor_hash(self, actor):
        x = hash(actor) % self.num_workers
        return x
        
    def schedule(self, target, event):
        """Schedule an event.

        An `event` is a thunk.

        """
        h = self.actor_hash(target)
        scheduler = self.schedulers[h]
        scheduler.enter(0, 1, event)

    def later(self, delay, event):
        self.scheduler.enter(delay, 1, event)
        
    def stop(self):
        """Stop the loop."""
        pass

    def run(self, block=False):
        for sched in self.schedulers:
            sched.run(blocking=block)

    def run_forever(self, wait=0.05):
        while True:
            self.run()
            time.sleep(wait)

    def run_sched_forever(self, sched, wait=0.00001):
        while True:
            sched.run(blocking=False)
            time.sleep(wait)

    def run_in_thread(self):
        self.threads = []
        for i, sched in enumerate(self.schedulers):
            thread = threading.Thread(target=self.run_sched_forever,
                                      args=(sched,),
                                      name='event_loop_{}'.format(i))
            thread.daemon = True
            thread.start()
            self.threads.append(thread)

        
