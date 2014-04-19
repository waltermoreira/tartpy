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

    def hash(self, actor):
        return int(hashlib.sha1(str(id(actor)).encode('utf8')).hexdigest(),
                   16) % self.num_workers
        
    def schedule(self, target, event):
        """Schedule an event.

        An `event` is a thunk.

        """
        h = self.hash(target)
        def tagged_event():
            print('executing in scheduler:', scheduler)
            print('in thread', threading.current_thread().name)
            event()
        scheduler = self.schedulers[h]
        scheduler.enter(0, 1, tagged_event)

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

    def run_sched_forever(self, sched, wait=0.05):
        while True:
            sched.run()
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

        
