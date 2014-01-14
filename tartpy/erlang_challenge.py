import time
import sys
from rt import Actor, initial_behavior

construction_start_time = 0
construction_end_time = 0
loop_completion_times = []

class RingLink(Actor):
    # args: next

    @initial_behavior
    def ringlink_beh(self, n):
        self.next(n)


class RingLast(Actor):
    # args: first
    
    @initial_behavior
    def ringlast_beh(self, n):
        loop_completion_times.append(time.time())
        if n > 1:
            self.first(n-1)
        else:
            self.behavior = self.sink_beh
            self.report()

    def sink_beh(self, message):
        pass

    def report(self):
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


class RingBuilder(Actor):
    # args: m

    @initial_behavior
    def ringbuilder_beh(self, message):
        if self.m > 0:
            next = RingBuilder.create(m=self.m-1)
            next(message)
            self.behavior = RingLink(next=next).behavior
        else:
            global construction_end_time
            construction_end_time = time.time()            
            message['first'](message['n'])
            self.behavior = RingLast(first=message['first']).behavior


def test(m, n):
    print('Starting {} actor ring'.format(m))
    global construction_start_time
    construction_start_time = time.time()
    ring = RingBuilder.create(m=m)
    ring({'first': ring, 'n': n})

if __name__ == '__main__':
    m = int(sys.argv[1])
    n = int(sys.argv[2])
    test(m, n)