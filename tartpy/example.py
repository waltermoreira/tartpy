import rt

class Stateless(rt.Actor):

    def __init__(self):
        super().__init__()
        self.behavior = self.stateless_beh

    def stateless_beh(self, message):
        print("Stateless got message: {}".format(message))
        

class Stateful(rt.Actor):

    def __init__(self, state):
        super().__init__()
        self.state = state
        self.behavior = self.stateful_beh
    
    def stateful_beh(self, message):
        print("Have state: {}".format(self.state))
        print("Stateful got message: {}".format(message))


class FlipFlop(rt.Actor):

    def __init__(self):
        super().__init__()
        self.behavior = self.first_beh
        
    def first_beh(self, message):
        print("First: {}".format(message))
        self.behavior = self.second_beh

    def second_beh(self, message):
        print("Second: {}".format(message))
        self.behavior = self.first_beh


class Chain(rt.Actor):

    def __init__(self, count):
        super().__init__()
        self.count = count
        self.behavior = self.chain_beh

    def chain_beh(self, message):
        if self.count > 0:
            print("Chain: {}".format(self.count))
            next = self.create(Chain, self.count - 1)
            next(message)

stateless = Stateless()
stateless('some message')
stateless('more message')

stateful = Stateful({'state': 5})
stateful({'some': 'other message'})
stateful(10)

flipflop = FlipFlop()
flipflop('first')
flipflop('second')
flipflop('third')
flipflop('fourth')

chain = Chain(10)
chain('go')