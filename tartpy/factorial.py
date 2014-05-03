import os
import sys
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))

from tartpy.runtime import Runtime, behavior
from tartpy.eventloop import EventLoop
from tartpy.example import print_beh

@behavior
def factorial_beh(self, msg):
    customer, n = msg
    if n == 0:
        customer << 1
    else:
        multiply_by_n = self.create(multiplier_beh, customer, n)
        self << (multiply_by_n, n-1)

@behavior
def multiplier_beh(customer, n, self, m):
    customer << m*n

def test(n):
    @behavior
    def print_and_stop_beh(self, message):
        print_beh(self, message)
        EventLoop().stop_later()

    runtime = Runtime()
    fac = runtime.create(factorial_beh)
    printer = runtime.create(print_and_stop_beh)
    fac << (printer, n)

if __name__ == '__main__':
    test(int(sys.argv[1]))
    EventLoop().run()
