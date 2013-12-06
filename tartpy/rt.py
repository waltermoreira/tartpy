import os
import multiprocessing
import threading

class Actor(object):

    def send(self, message, method='thread'):
        spawn(self.behavior, message, method)

    def create(self, actor, *args):
        return actor(*args)
    
def spawn(f, args, method='thread'):
    if method == 'thread':
        t = threading.Thread(target=f, args=(args,))
        t.start()
    if method == 'process':
        p = multiprocessing.Process(target=f, args=(args,))
        p.start()


class Stateless(Actor):

    def __init__(self):
        self.behavior = self.stateless_beh

    def stateless_beh(self, message):
        print("Got message: {}".format(message))
        

class Stateful(Actor):

    def __init__(self, state):
        self.state = state
        self.behavior = self.stateful_beh
    
    def stateful_beh(self, message):
        print("Have state: {}".format(self.state))
        print("Got message: {}".format(message))


class FlipFlop(Actor):

    def __init__(self):
        self.behavior = self.first_beh
        
    def first_beh(self, message):
        print("First: {}".format(message))
        self.behavior = self.second_beh

    def second_beh(self, message):
        print("Second: {}".format(message))
        self.behavior = self.first_beh


class Chain(Actor):

    def __init__(self, count):
        self.count = count
        self.behavior = self.chain_beh

    def chain_beh(self, message):
        if self.count > 0:
            self.count -= 1
            print("Chain: {}".format(self.count))
            next = self.create(Chain, self.count)
            next.send(message)
    