import queue
import threading


def individual_loop(queue, actor):
    while True:
        message = queue.get()
        actor.behavior(message)


        
def global_loop_step(queue, block=False):
    actor, message = queue.get(block=block)
    actor.behavior(message)


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
            
