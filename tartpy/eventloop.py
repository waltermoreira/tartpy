"""

Very basic implementation of an event loop
==========================================

The eventloop is a singleton to schedule and run events.

Exports
-------

- ``EventLoop``: the basic eventloop

"""

import asyncio
import queue
import sched
import threading
import time

from .singleton import Singleton


class EventLoop(object, metaclass=Singleton):

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.do = self.sync_do

    def sync_do(self, f, *args, **kwargs):
        f(*args, **kwargs)

    def thread_do(self, f, *args, **kwargs):
        self.loop.call_soon_threadsafe(f, *args, **kwargs)

    def schedule(self, target, event):
        self.do(self.loop.call_soon, event)

    def later(self, delay, event):
        self.do(self.loop.call_later, delay, event)

    def run(self):
        self.do = self.sync_do
        self.loop.run_forever()

    def run_once(self):
        self.stop_later()
        self.run()
        
    def run_in_thread(self):
        self.do = self.thread_do
        self.thread = threading.Thread(target=self.loop.run_forever,
                                       name='asyncio_event_loop')
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.loop.stop()

    def stop_later(self):
        self.do = self.sync_do
        self.schedule(self, self.stop)