import pytest

from tartpy.runtime import behavior, SimpleRuntime
from tartpy.eventloop import EventLoop


runtime = SimpleRuntime()


def test_runtime_error():

    err = False

    class TestRuntime(SimpleRuntime):

        def error(self, message):
            nonlocal err
            err = True

    @behavior
    def beh(self, msg):
        1/0

    test_rt = TestRuntime()
    x = test_rt.create(beh)
    x << 5
    EventLoop().run()
    assert err is True
    
    
def test_self_create():

    result = None
    
    @behavior
    def foo(self, msg):
        nonlocal result
        result = msg
        
    @behavior
    def beh(self, msg):
        a = self.create(foo)
        a << msg

    x = runtime.create(beh)
    x << 5
    EventLoop().run()
    assert result == 5
    

def test_receive_message():

    result = None
    
    @behavior
    def beh(self, msg):
        nonlocal result
        result = msg

    a = runtime.create(beh)
    a << 5
    EventLoop().run()
    assert result == 5

def test_create_with_args():

    result = None
    
    @behavior
    def beh(arg, self, msg):
        nonlocal result
        result = arg

    a = runtime.create(beh, True)
    a << 0
    EventLoop().run()
    assert result is True

def test_one_shot():

    sink_beh_done = False
    destination_beh_done = False
    message = None
    
    @behavior
    def one_shot_beh(destination, self, msg):
        destination << msg
        self.become(sink_beh)

    @behavior
    def sink_beh(self, msg):
        assert msg == 'second'
        nonlocal sink_beh_done
        sink_beh_done = True

    @behavior
    def destination_beh(self, msg):
        nonlocal message, destination_beh_done
        message = msg
        destination_beh_done = True

    destination = runtime.create(destination_beh)
    one_shot = runtime.create(one_shot_beh, destination)

    one_shot << 'first'
    one_shot << 'second'

    EventLoop().run()
    assert message == 'first'
    assert sink_beh_done and destination_beh_done
    
def test_serial():

    first_msg = second_msg = third_msg = None
    first_behavior = second_behavior = third_behavior = None
    first = second = third = None
    
    @behavior
    def first_beh(self, msg):
        self.become(second_beh)
        nonlocal first_msg, first_behavior, first
        first_msg = msg
        first_behavior = record()
        first = True

    @behavior
    def second_beh(self, msg):
        self.become(third_beh)
        nonlocal second_msg, second_behavior, second
        second_msg = msg
        second_behavior = record()
        second = True

    @behavior
    def third_beh(self, msg):
        nonlocal third_msg, third_behavior
        third_msg = msg
        third_behavior = record()

    def record():
        return bool(first), bool(second), bool(third)
        
    serial = runtime.create(first_beh)
    serial << 'foo'
    serial << 'foo'
    serial << 'foo'

    EventLoop().run()

    assert first_msg == 'foo' and second_msg == 'foo' and third_msg == 'foo'
    assert first_behavior == (False, False, False)
    assert second_behavior == (True, False, False)
    assert third_behavior == (True, True, False)

# @behavior
# def ringlink_beh(next, context, n):
#     next << n

# @behavior
# def ringlast_beh(first, context, n):
#     loop_completion_times.append(time.time())
#     if n > 1:
#         first << n-1
#     else:
#         context.become(sink_beh)
#         report()

# @behavior
# def sink_beh(context, msg):
#     pass

# @behavior
# def ringbuilder_beh(m, context, msg):
#     if m > 0:
#         next = context.create(ringbuilder_beh, m-1)
#         next << msg
#         context.become(ringlink_beh, next)
#     else:
#         global construction_end_time
#         construction_end_time = time.time()
#         msg['first'] << msg['n']
#         context.become(ringlast_beh, msg['first'])

# def erlang_challenge(m, n):
#     print('Starting {} actor ring'. format(m))
#     global construction_start_time
#     construction_start_time = time.time()
#     ring = runtime.create(ringbuilder_beh, m)
#     ring << {'first': ring, 'n': n}

# construction_start_time = 0
# construction_end_time = 0
# loop_completion_times = []

# def report():
#     print('Construction time: {} seconds'.format(
#         construction_end_time - construction_start_time))
#     print('Loop times:')
#     loop_completion_times.insert(0, construction_end_time)
#     intervals = [t1-t0
#                  for (t0, t1) in zip(loop_completion_times,
#                                      loop_completion_times[1:])]
#     for t in intervals:
#         print('  {} seconds'.format(t))
#     print('Average: {} seconds'.format(sum(intervals)/len(intervals)))

# if __name__ == '__main__':
#     erlang_challenge(int(sys.argv[1]), int(sys.argv[2]))
#     run_loop()