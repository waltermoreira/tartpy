"""

Actor Runtime
=============

The runtime provides the functions to create an actor from a behavior,
and to report an error.  Subclass from `AbstractRuntime` to create a
runtime class.

`SimpleRuntime.create` just creates the actor, and
`SimpleRuntime.throw` prints the error message to stdout.

The behaviors are defined as::

    @behavior
    def my_beh(arg1, ..., self, msg):
        ...

where `arg1, ...` are 0 or more arguments to be passed at creation
time. `self` refers to the actor in context, and `msg` is the message
being passed.

To create or change behavior, `self` provides the methods `create` and
`become`. To send a message to an actor `x` use `x << msg`.  For
example::

    @behavior
    def my_beh(n, self, msg):
        if n > 0:
            another = self.create(my_beh, n-1)
            another << 'a message'
        self.become(sink_beh)

    @behavior
    def sink_beh(self, msg):
        pass

"""

from collections.abc import MutableMapping
from functools import wraps, partial
import pprint
import sys
import traceback

from .singleton import Singleton
from .eventloop import EventLoop


class AbstractRuntime(object, metaclass=Singleton):

    def create(self, behavior, *args):
        raise NotImplementedError()

    def throw(self, message):
        raise NotImplementedError()


class SimpleRuntime(AbstractRuntime):

    def __init__(self):
        super().__init__()
        self.loop = EventLoop()
        
    def create(self, behavior, *args):
        return Actor(self, behavior, *args)

    def throw(self, message):
        print('ERROR: {0}'.format(pprint.pformat(message)))


class Runtime(SimpleRuntime):

    def throw(self, message):
        super().throw(message)
        # also display human readable traceback, if possible
        try:
            print('\n' + ''.join(message['traceback']))
        except (TypeError, KeyError):
            pass


class ThreadedRuntime(Runtime):

    def __init__(self):
        super().__init__()
        self.restart()

    def pause(self):
        self.evloop.stop()

    def restart(self):
        self.evloop = EventLoop()
        self.evloop.run_in_thread()
        

def exception_message():
    """Create a message with details on the exception."""
    exc_type, exc_value, exc_tb = exc_info = sys.exc_info()
    return {'exception': {'type': exc_type,
                          'value': exc_value,
                          'traceback': exc_tb},
            'traceback': traceback.format_exception(*exc_info)}
    

class Actor(object):

    def __init__(self, runtime, behavior, *args):
        self._runtime = runtime
        self.become(behavior, *args)
        self._loop = self._runtime.loop

    def become(self, behavior, *args):
        self._behavior = partial(behavior, *args)

    def send(self, msg):
        def event():
            try:
                self._behavior(self, msg)
            except Exception as exc:
                self.throw(exception_message())
        self._loop.schedule(self, event)

    def create(self, behavior, *args):
        return self._runtime.create(behavior, *args)

    def throw(self, message):
        self._runtime.throw(message)

    def __lshift__(self, msg):
        """Syntax sugar for sending a message.

        Use as `x << msg`.

        """
        self.send(msg)
        
    def __call__(self, msg):
        self.send(msg)


class Message(dict):

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def behavior(f):
    """Decorator for declaring a function as behavior.

    Use as::

        @behavior
        def fun(x, y, self, msg):
            ...

    And create or become this behavior by passing the two arguments
    `x` and `y`.

    """
    @wraps(f)
    def wrapper(*args):
        message = args[-1]
        if isinstance(message, MutableMapping):
            message = Message(message)
        f(*(args[:-1] + (message,)))
    return wrapper

