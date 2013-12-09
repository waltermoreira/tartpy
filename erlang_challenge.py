import sys
import rt

class RingLink(rt.Actor):

    def __init__(self, next):
        super().__init__()
        self.next = next
        self.behavior = self.ringlink_beh

    def ringlink_beh(self, n):
        print('Link. msg =', n)
        self.next(n)


class RingLast(rt.Actor):

    def __init__(self, first):
        super().__init__()
        self.first = first
        self.behavior = self.ringlast_beh

    def ringlast_beh(self, n):
        if n > 1:
            print('Last. msg =', n)
            self.first(n-1)
        else:
            self.behavior = self.sink_beh
            self.report()

    def sink_beh(self, message):
        pass

    def report(self):
        print('End')


class RingBuilder(rt.Actor):

    def __init__(self, m):
        super().__init__()
        self.m = m
        self.behavior = self.ringbuilder_beh

    def ringbuilder_beh(self, message):
        if self.m > 0:
            print('m =', self.m)
            next = RingBuilder.create(self.m-1)
            next(message)
            self.behavior = RingLink(next).behavior
        else:
            message['first'](message['n'])
            self.behavior = RingLast(message['first']).behavior


def test(m, n):
    ring = RingBuilder.create(m)
    ring({'first': ring, 'n': n})

if __name__ == '__main__':
    m = int(sys.argv[1])
    n = int(sys.argv[2])
    test(m, n)