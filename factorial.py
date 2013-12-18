import rt

class Factorial(rt.Actor):

    def __init__(self):
        super().__init__()
        self.behavior = self.factorial_beh

    def factorial_beh(self, message):
        customer, n = message
        if n == 0:
            customer(1)
        else:
            multiply_by_n = Multiplier.create(customer, n)
            self((multiply_by_n, n-1))


class Multiplier(rt.Actor):

    def __init__(self, customer, n):
        super().__init__()
        self.customer = customer
        self.n = n
        self.behavior = self.multiplier_beh

    def multiplier_beh(self, m):
        self.customer(m * self.n)
        