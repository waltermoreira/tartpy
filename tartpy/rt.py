import os
import multiprocessing
import threading

class Sponsor(object):

    def __init__(self):
        print('Sponsor pid: {}'.format(os.getpid()))

    def create(self, behavior):
        return Actor(behavior, self)

class Actor(object):

    def __init__(self, behavior, sponsor):
        self.behavior = behavior
        self.sponsor = sponsor

    def send(self, message):
        spawn(self.behavior, message, method='process')


def spawn(f, args, method='thread'):
    if method == 'thread':
        t = threading.Thread(target=f, args=(args,))
        t.start()
    if method == 'process':
        p = multiprocessing.Process(target=f, args=(args,))
        p.start()

