from rt import Actor, initial_behavior

class Factorial(Actor):

    @initial_behavior
    def factorial_beh(self, message):
        customer, n = message
        if n == 0:
            customer(1)
        else:
            multiply_by_n = Multiplier.create(customer=customer, n=n)
            self((multiply_by_n, n-1))


class Multiplier(Actor):

    @initial_behavior
    def multiplier_beh(self, m):
        self.customer(m * self.n)
        