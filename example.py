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
            next = Chain.create(self.count - 1)
            next(message)

            
class Echo(rt.Actor):

    def __init__(self):
        super().__init__()
        self.behavior = self.echo_beh

    def echo_beh(self, message):
        message['reply_to']({'answer': message})

        
class Printer(rt.Actor):
    
    def __init__(self):
        super().__init__()
        self.behavior = self.print_beh

    def print_beh(self, message):
        print('Got', message)
        

def test():
    stateless = Stateless.create()
    stateless('some message')
    stateless('more message')

    stateful = Stateful.create({'state': 5})
    stateful({'some': 'other message'})
    stateful(10)

    flipflop = FlipFlop.create()
    flipflop('first')
    flipflop('second')
    flipflop('third')
    flipflop('fourth')

    chain = Chain.create(10)
    chain('go')

    echo = Echo.create()
    printer = Printer.create()
    echo({'reply_to': printer})


if __name__ == '__main__':
    test()