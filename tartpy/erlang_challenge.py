import os
import sys
import time

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))

from tartpy.runtime import behavior, SimpleRuntime, Runtime
from tartpy.eventloop import EventLoop

construction_start_time = 0
construction_end_time = 0
loop_completion_times = []


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
        next = self.create(ringbuilder_beh, m-1)
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
    runtime = Runtime()
    construction_start_time = time.time()
    ring = runtime.create(ringbuilder_beh, m)
    ring << {'first': ring, 'n': n}

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


if __name__ == '__main__':
    m = int(sys.argv[1])
    n = int(sys.argv[2])
    erlang_challenge(m, n)
    time.sleep(20)
#    EventLoop().run_forever()