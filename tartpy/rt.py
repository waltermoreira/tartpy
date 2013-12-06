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

        
sponsor = Sponsor()


def stateless_beh(message):
    print("Got message: {}".format(message))
    
stateless = sponsor.create(stateless_beh)


def stateful_beh(state):
    def _f(message):
        print("Have state: {}".format(state))
        print("Got message: {}".format(message))
    return _f

stateful = sponsor.create(stateful_beh({'key': 5}))


    