import queue
import threading


def indiviual_loop(queue, actor):
    while True:
        message = queue.get()
        actor.behavior(message)


def global_loop(queue):
    while True:
        actor, message = queue.get()
        actor.behavior(message)


def initial_behavior(f):
    f.initial_behavior = True
    return f
        

class MetaActor(type):

    def __new__(mcls, name, bases, dict):
        for meth in list(dict.values()):
            if getattr(meth, 'initial_behavior', False):
                dict['behavior'] = meth
        return type.__new__(mcls, name, bases, dict)
        
        
class EventLoop(object):

    loop = None
    
    def __init__(self):
        self.queue = queue.Queue()
        self.thread = threading.Thread(
            target=global_loop,
            args=(self.queue,),
            name='global-loop')
        self.thread.start()

    def schedule(self, message, target):
        self.queue.put((target, message))
        
    @classmethod
    def get_loop(cls):
        if cls.loop is None:
            cls.loop = cls()
        return cls.loop
                    

class AbstractActor(object, metaclass=MetaActor):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        
    def __call__(self, message):
        self._put(message)

    def _put(self, message):
        raise NotImplementedError()

    def _ensure_loop(self):
        pass
        
    @classmethod
    def create(cls, *args, **kwargs):
        sponsor = kwargs.pop('sponsor', None)
        if sponsor is not None:
            return sponsor.create(cls, *args, **kwargs)
        else:
            actor = cls(*args)
            actor._ensure_loop()
            return actor


class ActorOwnLoop(AbstractActor):

    def _put(self, message):
        self.queue.put(message)
        
    def _ensure_loop(self):
        self.queue = queue.Queue()
        self.dispatcher = threading.Thread(
            target=indiviual_loop,
            args=(self.queue, self),
            name=self._thread_name())
        self.dispatcher.start()

    def _thread_name(self):
        return '{}-{}'.format(
            self.__class__.__name__,
            hex(id(self)))
        
        
class ActorGlobalLoop(AbstractActor):

    def _put(self, message):
        self.loop.schedule(message, self)

    def _ensure_loop(self):
        self.loop = EventLoop.get_loop()


Actor = ActorGlobalLoop
