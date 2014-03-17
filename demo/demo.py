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

# ------------------------------

# Actor idioms
# - Dale Schumacher's Actor Idioms paper:
#   https://apice.unibo.it/xwiki/bin/download/AGERE2012/AcceptedPapers/ageresplash2012submission3.pdf
    
# ------------------------------

# Request/reply example
    
@behavior
def service_beh(self, message):
    customer = message['customer']
    customer << 'some data'

@behavior
def log_beh(self, message):
    print('CUSTOMER:')
    print(message)

service = runtime.create(service_beh)
log = runtime.create(log_beh)

def test_service():
    service << {'customer': log}

# ------------------------------

# Forward example
# Forwards all messages to the subject

@behavior
def forward_beh(subject, self, message):
    subject << message

forward = runtime.create(forward_beh, log)

def test_forward():
    forward << 'hi'
    forward << 'there'

# ------------------------------

# One-shot example
# Forward only a simple message

@behavior
def one_shot_beh(subject, self, message):
    subject << message
    self.become(ignore_beh)

@behavior
def ignore_beh(self, message):
    pass

one_shot = runtime.create(one_shot_beh, log)

def test_one_shot():
    one_shot << 'are we there yet?'
    one_shot << 'are we there yet?'
    one_shot << 'are we there yet?'