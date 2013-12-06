import multiprocessing
import threading

class Actor(object):

    def _spawn_method(self):
        return threading.Thread
        # return multiprocessing.Process

    def __call__(self, message):
        spawn = self._spawn_method()
        spawn(target=self.behavior, args=(message,)).start()

    def create(self, actor, *args):
        return actor(*args)
