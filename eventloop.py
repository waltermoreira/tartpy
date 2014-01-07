import queue
import sys
import threading
import traceback


def _format_exception(exc_info):
    exc_type, exc_value, exc_tb = exc_info
    return {'exception': {'type': exc_type,
                          'value': exc_value,
                          'traceback': exc_tb},
            'traceback': traceback.format_exception(*exc_info)}
    

def individual_loop_step(queue, actor, block=True):
    message = queue.get(block=block)
    try:
        return actor.behavior(message)
    except Exception as exc:
        err = _format_exception(sys.exc_info())
        actor.error(err)
        return err

    
def individual_loop(queue, actor):
    while True:
        individual_loop_step(queue, actor)

        
def global_loop_step(queue, block=False):
    actor, message = queue.get(block=block)
    try:
        actor.behavior(message)
    except Exception as exc:
        actor.error(_format_exception(sys.exc_info()))


def global_loop(queue):
    while True:
        global_loop_step(queue, block=True)


class EventLoop(object):

    loop = None

    def __init__(self):
        self.queue = queue.Queue()

    def schedule(self, message, target):
        self.queue.put((target, message))

    @classmethod
    def get_loop(cls):
        if cls.loop is None:
            cls.loop = cls()
        return cls.loop
        

class ThreadedEventLoop(EventLoop):

    def __init__(self):
        super().__init__()
        self.thread = threading.Thread(
            target=global_loop,
            args=(self.queue,),
            name='global-loop')
        self.thread.start()


class ManualEventLoop(EventLoop):

    def run(self):
        try:
            while True:
                global_loop_step(self.queue)
        except queue.Empty:
            return
            
