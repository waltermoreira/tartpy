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
import traceback


def _format_exception(exc_info):
    """Create a message with details on the exception."""
    exc_type, exc_value, exc_tb = exc_info
    return {'exception': {'type': exc_type,
                          'value': exc_value,
                          'traceback': exc_tb},
            'traceback': traceback.format_exception(*exc_info)}
    

def individual_loop_step(queue, actor, block=True):
    """Process one event for ``actor``.

    The argument ``block`` decides whether to block or not when there
    are no messages.  Any exception in the behaviors is reported
    through the error mechanism of the actor.

    """
    message = queue.get(block=block)
    try:
        return actor.behavior(message)
    except Exception as exc:
        err = _format_exception(sys.exc_info())
        actor.error(err)
        return err

    
def individual_loop(queue, actor):
    """Process events for ``actor`` indefinitely."""
    while True:
        individual_loop_step(queue, actor)

        
def global_loop_step(queue, block=False):
    """Global event loop step.

    Process one event extracted from the queue.
    
    """
    actor, message = queue.get(block=block)
    try:
        actor.behavior(message)
    except Exception as exc:
        actor.error(_format_exception(sys.exc_info()))


def global_loop(queue):
    """Process events indefinitely."""
    while True:
        global_loop_step(queue, block=True)


class EventLoop(object):
    """A generic event loop object.

    An ``EventLoop`` is a singleton.  Get an instance with::

        EventLoop.get_loop()

    """

    loop = None

    def __init__(self):
        self.queue = queue.Queue()

    def schedule(self, message, target):
        """Schedule an event."""
        self.queue.put((target, message))

    @classmethod
    def get_loop(cls):
        """Obtain a loop.

        Start a new one if necessary.

        """
        if cls.loop is None:
            cls.loop = cls()
        return cls.loop
        

class ThreadedEventLoop(EventLoop):
    """An event loop that dispatches events from a thread."""

    def __init__(self):
        super().__init__()
        self.thread = threading.Thread(
            target=global_loop,
            args=(self.queue,),
            name='global-loop')
        self.thread.start()


class ManualEventLoop(EventLoop):
    """An event loop that needs to be run explicitly."""

    def run(self):
        """Process all events in the queue until empty.

        It doesn't block if the queue is empty.

        """
        try:
            while True:
                global_loop_step(self.queue)
        except queue.Empty:
            return
            
