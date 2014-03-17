"""Tartpy demo.

Suggestions to play with this demo:

- Install `tartpy`
- Run `[i]python` from the `demo` directory, and `import demo`
- Run already built tests (for example: `demo.test_counter()`)
- Interact with the actors by sending them messages, for example::

     counter << 5

"""

from tartpy.runtime import Runtime, behavior

# The runtime is responsible for initially creating the actors
runtime = Runtime()

# ------------------------------

# An actor in Python:
# A behavior gets:
# - `self`: the actor that is executing this behavior,
# - `message`: the message being passed.

@behavior
def demo_beh(self, message):
    print(message)

# Construct the actor with behavior `demo_beh`

demo_actor = runtime.create(demo_beh)

# and send it a message

def test_demo_actor():
    demo_actor << 'foo'

# ------------------------------

# An actor with state:
# The first argument `state` is mutated for each message the actor
# receives.

@behavior
def counter_beh(state, self, message):
    print('Start count:', state['count'])
    print('Message:    ', message)

    state['count'] += message

    print('End count:  ', state['count'])

# Create actor with inital state.
    
counter = runtime.create(counter_beh, {'count': 1337})

# And test it with some messages

def test_counter():
    counter << 1
    counter << 2
    counter << -10

# ------------------------------

# Ping-pong example.
# Notice the messages are asynchronous.

@behavior
def ping_beh(self, message):
    print('[PING****] send')
    message << self
    print('[PING****] finish')

@behavior
def pong_beh(state, self, message):
    if state['count'] == 0:
        print('[****PONG] Done')
        return

    print('[****PONG] send')
    message << self
    print('[****PONG] finish')
    state['count'] -= 1

ping = runtime.create(ping_beh)
pong = runtime.create(pong_beh, {'count': 2})

def test_ping_pong():
    ping << pong

# ------------------------------

# Show methods available to the actor `self`.
# In addition to `send`, `create`, and `become`,
# the method `throw` raises an error to the runtime.
    
@behavior
def show_self_beh(self, message):
    print('self:', self)
    print('methods:', [meth for meth in dir(self) if not meth.startswith('_')])

show_self = runtime.create(show_self_beh)

def test_show_self():
    show_self << None

# ------------------------------

# Simple example of `become`
    
@behavior
def say_red_beh(self, message):
    print('[SAYING]: red')
    self.become(say_black_beh)

@behavior
def say_black_beh(self, message):
    print('[SAYING]: black')
    self.become(say_red_beh)

say = runtime.create(say_red_beh)

def test_say():
    say << None

# ------------------------------

# Changing behaviors with state:
    
@behavior
def flip_up_beh(state, self, message):
    print(state, 'flipping up...')
    self.become(flip_down_beh, 'up')

@behavior
def flip_down_beh(state, self, message):
    print(state, 'flipping down...')
    self.become(flip_up_beh, 'down')

flipper = runtime.create(flip_down_beh, 'neither')

def test_flipper():
    flipper << None
    flipper << None
    flipper << None

