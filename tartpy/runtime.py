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

from functools import wraps
import pprint

from .singleton import Singleton
from .eventloop import EventLoop


class AbstractRuntime(object, metaclass=Singleton):

    def create(self, behavior, *args):
        raise NotImplementedError()

    def throw(self, message):
        raise NotImplementedError()


class SimpleRuntime(AbstractRuntime):

    def create(self, behavior, *args):
        return Actor(self, behavior, *args)

    def throw(self, message):
        print('ERROR: {0}'.format(pprint.pformat(message)))


class Runtime(SimpleRuntime):

    def __init__(self):
        super().__init__()
        self.evloop = EventLoop()
        self.evloop.run_in_thread()
        
    def throw(self, message):
        super().throw(message)
        # also display human readable traceback, if possible
        try:
            print('\n' + ''.join(message['traceback']))
        except (TypeError, KeyError):
            pass

        
class Actor(object):

    def __init__(self, runtime, behavior, *args):
        self._runtime = runtime
        self.become(behavior, *args)
        self._ev_loop = EventLoop()

    def become(self, behavior, *args):
        self._behavior = behavior(*args)

    def send(self, msg):
        def event():
            try:
                self._behavior(self, msg)
            except Exception as exc:
                self.throw(exception_message())
        self._ev_loop.schedule(event)

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
        def _f(self, msg):
            f(*(args + (self, msg)))
        return _f
    return wrapper

