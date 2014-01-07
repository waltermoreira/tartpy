import queue
import threading

import eventloop


def initial_behavior(f):
    f.initial_behavior = True
    return f
        

class MetaActor(type):

    def __new__(mcls, name, bases, dict):
        for meth in list(dict.values()):
            if getattr(meth, 'initial_behavior', False):
                dict['behavior'] = meth
        return type.__new__(mcls, name, bases, dict)
        
        
class AbstractActor(object, metaclass=MetaActor):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self._ensure_loop()
        
    def __call__(self, message):
        raise NotImplementedError()

    def _ensure_loop(self):
        pass

    def error(self, message):
        if self.sponsor is not None:
            self.sponsor.error(self, message)
        else:
            self._error(message)

    def _error(self, message):
        print('ERROR: {0}'.format(message))
            
    @classmethod
    def create(cls, **kwargs):
        sponsor = kwargs.get('sponsor', None)
        if sponsor is not None:
            return sponsor.create(cls, **kwargs)
        else:
            actor = cls(**kwargs)
            return actor


class ActorOwnLoop(AbstractActor):

    def __call__(self, message):
        self.queue.put(message)
        
    def _ensure_loop(self):
        self.queue = queue.Queue()
        self.dispatcher = threading.Thread(
            target=eventloop.individual_loop,
            args=(self.queue, self),
            name=self._thread_name())
        self.dispatcher.start()

    def _thread_name(self):
        return '{}-{}'.format(
            self.__class__.__name__,
            hex(id(self)))
        
        
class ActorGlobalLoop(AbstractActor):

    def __call__(self, message):
        self.loop.schedule(message, self)

    def _ensure_loop(self):
        self.loop = eventloop.ThreadedEventLoop.get_loop()


class ActorManualLoop(AbstractActor):

    def __call__(self, message):
        self.loop.schedule(message, self)
    
    def _ensure_loop(self):
        self.loop = eventloop.ManualEventLoop.get_loop()

    def run(self):
        self.loop.run()
        

class ActorOwnManualLoop(AbstractActor):

    def __call__(self, message):
        self.queue.put(message)

    def _ensure_loop(self):
        self.queue = queue.Queue()
        
    def run(self):
        eventloop.individual_loop(self.queue, self)

    def act(self):
        return eventloop.individual_loop_step(self.queue, self)
        

class Wait(ActorOwnManualLoop):

    @initial_behavior
    def wait_beh(self, message):
        return message
        
        
Actor = ActorOwnLoop
#Actor = ActorGlobalLoop
#Actor = ActorManualLoop