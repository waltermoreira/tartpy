import threading
import time
import queue
from functools import wraps, partial
import sys
import traceback


def _format_exception(exc_info):
    """Create a message with details on the exception."""
    exc_type, exc_value, exc_tb = exc_info
    return {'exception': {'type': exc_type,
                          'value': exc_value,
                          'traceback': exc_tb},
            'traceback': traceback.format_exception(*exc_info)}

def behavior(f):
    @wraps(f)
    def wrapper(*args):
        def _f(context, msg):
            f(*(args + (context, msg)))
        return _f
    return wrapper

@behavior
def bar(context, msg):
    print("i'm bar", msg)

@behavior
def foo(n, context, msg):
    print(n, context, msg)
    context.become(bar)

@behavior
def gii(context, n):
    print('gii got', n)
    if n > 0:
        context.self << n-1
    else:
        print('finally')
        a = context.create(foo, 3)
        a << 5
    
q = queue.Queue()

def beh_loop(queue, block=True):
    try:
        while True:
            context, msg = queue.get(block=block)
            try:
                context._behavior(context, msg)
            except Exception as exc:
                print(_format_exception(sys.exc_info()))
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

class AbstractRuntime(object):

    def create(self, behavior, *args):
        raise NotImplementedError()


class SimpleRuntime(AbstractRuntime):

    def create(self, behavior, *args):
        a = Context(self, behavior, *args)
        return Actor(a.send)

runtime = SimpleRuntime()

    
class Context(object):

    def __init__(self, runtime, behavior, *args):
        self.runtime = runtime
        self.self = Actor(self.send)
        self.become(behavior, *args)

    def become(self, behavior, *args):
        self._behavior = behavior(*args)

    def send(self, msg):
        q.put((self, msg))

    def create(self, behavior, *args):
        return self.runtime.create(behavior, *args)

        
class Actor(object):

    def __init__(self, f):
        self.f = f

    def __lshift__(self, msg):
        self.f(msg)


def test_context_create():

    result = None
    
    @behavior
    def foo(ctx, msg):
        nonlocal result
        result = msg
        
    @behavior
    def beh(ctx, msg):
        a = ctx.create(foo)
        a << msg

    x = runtime.create(beh)
    x << 5
    run_loop()
    assert result == 5
    
def test_receive_message():

    result = None
    
    @behavior
    def beh(context, msg):
        nonlocal result
        result = msg

    a = runtime.create(beh)
    a << 5
    run_loop()
    assert result == 5

def test_create_with_args():

    result = None
    
    @behavior
    def beh(arg, context, msg):
        nonlocal result
        result = arg

    a = runtime.create(beh, True)
    a << 0
    run_loop()
    assert result is True

def test_one_shot():

    sink_beh_done = False
    destination_beh_done = False
    message = None
    
    @behavior
    def one_shot_beh(destination, context, msg):
        destination << msg
        context.become(sink_beh)

    @behavior
    def sink_beh(context, msg):
        assert msg == 'second'
        nonlocal sink_beh_done
        sink_beh_done = True

    @behavior
    def destination_beh(context, msg):
        nonlocal message, destination_beh_done
        message = msg
        destination_beh_done = True

    destination = runtime.create(destination_beh)
    one_shot = runtime.create(one_shot_beh, destination)

    one_shot << 'first'
    one_shot << 'second'

    run_loop()
    assert message == 'first'
    assert sink_beh_done and destination_beh_done
    
def test_serial():

    first_msg = second_msg = third_msg = None
    first_behavior = second_behavior = third_behavior = None
    first = second = third = None
    
    @behavior
    def first_beh(context, msg):
        context.become(second_beh)
        nonlocal first_msg, first_behavior, first
        first_msg = msg
        first_behavior = record()
        first = True

    @behavior
    def second_beh(context, msg):
        context.become(third_beh)
        nonlocal second_msg, second_behavior, second
        second_msg = msg
        second_behavior = record()
        second = True

    @behavior
    def third_beh(context, msg):
        nonlocal third_msg, third_behavior
        third_msg = msg
        third_behavior = record()

    def record():
        return bool(first), bool(second), bool(third)
        
    serial = runtime.create(first_beh)
    serial << 'foo'
    serial << 'foo'
    serial << 'foo'

    run_loop()

    assert first_msg == 'foo' and second_msg == 'foo' and third_msg == 'foo'
    assert first_behavior == (False, False, False)
    assert second_behavior == (True, False, False)
    assert third_behavior == (True, True, False)

@behavior
def ringlink_beh(next, context, n):
    next << n

@behavior
def ringlast_beh(first, context, n):
    loop_completion_times.append(time.time())
    if n > 1:
        first << n-1
    else:
        context.become(sink_beh)
        report()

@behavior
def sink_beh(context, msg):
    pass

@behavior
def ringbuilder_beh(m, context, msg):
    if m > 0:
        next = context.create(ringbuilder_beh, m-1)
        next << msg
        context.become(ringlink_beh, next)
    else:
        global construction_end_time
        construction_end_time = time.time()
        msg['first'] << msg['n']
        context.become(ringlast_beh, msg['first'])

def erlang_challenge(m, n):
    print('Starting {} actor ring'. format(m))
    global construction_start_time
    construction_start_time = time.time()
    ring = runtime.create(ringbuilder_beh, m)
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
