import os
import sys
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))

from tartpy.runtime import behavior, SimpleRuntime
from tartpy.eventloop import EventLoop

@behavior
def stateless_beh(self, message):
    print("Stateless got message: {}".format(message))
        

@behavior
def stateful_beh(state, self, message):
    print("Have state: {}".format(state))
    print("Stateful got message: {}".format(message))


@behavior
def flipflop_first_beh(self, message):
    print("First: {}".format(message))
    self.become(flipflop_second_beh)

@behavior
def flipflop_second_beh(self, message):
    print("Second: {}".format(message))
    self.become(flipflop_first_beh)


@behavior
def chain_beh(count, self, message):
    if count > 0:
        print("Chain: {}".format(count))
        next = self.create(chain_beh, count-1)
        next << message

@behavior
def echo_beh(self, message):
    message['reply_to'] << {'answer': message}

@behavior
def print_beh(self, message):
    print('Got', message)
        

def test():
    runtime = SimpleRuntime()
    
    stateless = runtime.create(stateless_beh)
    stateless << 'some message'
    stateless << 'more message'

    stateful = runtime.create(stateful_beh, {'key': 5})
    stateful << {'some': 'other message'}
    stateful << 10

    flipflop = runtime.create(flipflop_first_beh)
    flipflop << 'first'
    flipflop << 'second'
    flipflop << 'third'
    flipflop << 'fourth'

    chain = runtime.create(chain_beh, 10)
    chain << 'go'

    echo = runtime.create(echo_beh)
    printer = runtime.create(print_beh)
    echo << {'reply_to': printer}


if __name__ == '__main__':
    test()
    EventLoop().run()
