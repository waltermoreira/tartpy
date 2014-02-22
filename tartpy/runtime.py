from functools import wraps
import pprint

from .singleton import Singleton
from .eventloop import EventLoop


class AbstractRuntime(object, metaclass=Singleton):

    def create(self, behavior, *args):
        raise NotImplementedError()

    def error(self, message):
        raise NotImplementedError()


class SimpleRuntime(AbstractRuntime):

    def create(self, behavior, *args):
        return Actor(self, behavior, *args)

    def error(self, message):
        print('ERROR: {0}'.format(pprint.pformat(message)))

        
class Actor(object):

    def __init__(self, runtime, behavior, *args):
        self.runtime = runtime
        self.become(behavior, *args)
        self.ev_loop = EventLoop()

    def become(self, behavior, *args):
        self._behavior = behavior(*args)

    def send(self, msg):
        def event():
            self._behavior(self, msg)
        self.ev_loop.schedule((event, self.error))

    def create(self, behavior, *args):
        return self.runtime.create(behavior, *args)

    def error(self, message):
        self.runtime.error(message)

    def __lshift__(self, msg):
        self.send(msg)
        

def behavior(f):
    @wraps(f)
    def wrapper(*args):
        def _f(self, msg):
            f(*(args + (self, msg)))
        return _f
    return wrapper

