import time
import sys
import rt

construction_start_time = 0
construction_end_time = 0
loop_completion_times = []

class RingLink(rt.Actor):

    def __init__(self, next):
        super().__init__()
        self.next = next
        self.behavior = self.ringlink_beh

    def ringlink_beh(self, n):
        self.next(n)


class RingLast(rt.Actor):

    def __init__(self, first):
        super().__init__()
        self.first = first
        self.behavior = self.ringlast_beh

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


class RingBuilder(rt.Actor):

    def __init__(self, m):
        super().__init__()
        self.m = m
        self.behavior = self.ringbuilder_beh

    def ringbuilder_beh(self, message):
        if self.m > 0:
            next = RingBuilder.create(self.m-1)
            next(message)
            self.behavior = RingLink(next).behavior
        else:
            global construction_end_time
            construction_end_time = time.time()            
            message['first'](message['n'])
            self.behavior = RingLast(message['first']).behavior


def test(m, n):
    print('Starting {} actor ring'.format(m))
    global construction_start_time
    construction_start_time = time.time()
    ring = RingBuilder.create(m)
    ring({'first': ring, 'n': n})

if __name__ == '__main__':
    m = int(sys.argv[1])
    n = int(sys.argv[2])
    test(m, n)