import threading
import time
import queue
from functools import wraps, partial

from . import eventloop


def behavior(f):
    @wraps(f)
    def wrapper(*args):
        def _f(context, msg):
            f(*(args + (context, msg)))
        return _f
    return wrapper

@behavior
def bar(self, msg):
    print("i'm bar", msg)

@behavior
def foo(n, self, msg):
    print(n, self, msg)
    self.become(bar())

q = queue.Queue()

def beh_loop(queue, block=True):
    try:
        while True:
            actor, msg = queue.get(block=block)
            try:
                actor._behavior(actor, msg)
            except Exception as exc:
                print(eventloop._format_exception(sys.exc_info()))
    except StopIteration:
        return

def run_loop():
    try:
        beh_loop(q, block=False)
    except queue.Empty:
        return
            
# loop = threading.Thread(
#     target=beh_loop,
#     args=(queue,),
#     name='beh_loop')
#loop.start()
    
class Actor(object):

    def __init__(self, behavior, *args):
        self.become(behavior, *args)

    def become(self, behavior, *args):
        self._behavior = behavior(*args)

    def send(self, msg):
        q.put((self, msg))

    def __lshift__(self, msg):
        self.send(msg)
        

def test_receive_message():

    @behavior
    def beh(self, msg):
        self.message = msg

    a = Actor(beh)
    a << 5
    run_loop()
    assert a.message == 5

def test_create_with_args():

    @behavior
    def beh(arg, self, msg):
        self.arg = arg

    a = Actor(beh, True)
    a << 0
    run_loop()
    assert a.arg is True

def test_one_shot():

    @behavior
    def one_shot_beh(destination, self, msg):
        destination.send(msg)
        self.become(sink_beh)

    @behavior
    def sink_beh(self, msg):
        assert msg == 'second'
        self.sink_beh_done = True

    @behavior
    def destination_beh(self, msg):
        self.msg = msg
        self.destination_beh_done = True

    destination = Actor(destination_beh)
    one_shot = Actor(one_shot_beh, destination)

    one_shot << 'first'
    one_shot << 'second'

    run_loop()
    assert destination.msg == 'first'
    assert one_shot.sink_beh_done and destination.destination_beh_done
    
def test_serial():

    @behavior
    def first_beh(self, msg):
        self.become(second_beh)
        self.first_msg = msg
        self.first_behavior = record(self)
        self.first = True

    @behavior
    def second_beh(self, msg):
        self.become(third_beh)
        self.second_msg = msg
        self.second_behavior = record(self)
        self.second = True

    @behavior
    def third_beh(self, msg):
        self.third_msg = msg
        self.third_behavior = record(self)

    def record(actor):
        return bool(actor.first), bool(actor.second), bool(actor.third)
        
    serial = Actor(first_beh)
    serial.first = serial.second = serial.third = False
    serial << 'foo'
    serial << 'foo'
    serial << 'foo'

    run_loop()

    assert serial.first_msg == 'foo' and serial.second_msg == 'foo' and serial.third_msg == 'foo'
    assert serial.first_behavior == (False, False, False)
    assert serial.second_behavior == (True, False, False)
    assert serial.third_behavior == (True, True, False)

@behavior
def ringlink_beh(next, self, n):
    next << n

@behavior
def ringlast_beh(first, self, n):
    loop_completion_times.append(time.time())
    if n > 1:
        first << n-1
    else:
        self.become(sink_beh)
        report()

@behavior
def sink_beh(self, msg):
    pass

@behavior
def ringbuilder_beh(m, self, msg):
    if m > 0:
        next = Actor(ringbuilder_beh, m-1)
        next << msg
        self.become(ringlink_beh, next)
    else:
        global construction_end_time
        construction_end_time = time.time()
        msg['first'] << msg['n']
        self.become(ringlast_beh, msg['first'])

def erlang_challenge(m, n):
    print('Starting {} actor ring'. format(m))
    global construction_start_time
    construction_start_time = time.time()
    ring = Actor(ringbuilder_beh, m)
    ring << {'first': ring, 'n': n}

construction_start_time = 0
construction_end_time = 0
loop_completion_times = []

def report():
    print('Construction time: {} seconds'.format(
        construction_end_time - construction_start_time))
    print('Loop times:')
    loop_completion_times.insert(0, construction_end_time)
    intervals = [t1-t0
                 for (t0, t1) in zip(loop_completion_times,
                                     loop_completion_times[1:])]
    for t in intervals:
        print('  {} seconds'.format(t))
    print('Average: {} seconds'.format(sum(intervals)/len(intervals)))
