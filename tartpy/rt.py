import queue
import multiprocessing
import threading

def loop(queue, actor):
    while True:
        message = queue.get()
        actor.behavior(message)
    
class Actor(object):

    def __init__(self):
        self.queue = queue.Queue()
        self.dispatcher = threading.Thread(
            target=loop,
            args=(self.queue, self))
        self.dispatcher.start()

    def __call__(self, message):
        self.queue.put(message)

    def create(self, actor, *args):
        return actor(*args)
