from .rt import Actor, initial_behavior


class Stateless(Actor):

    @initial_behavior
    def stateless_beh(self, message):
        print("Stateless got message: {}".format(message))
        

class Stateful(Actor):

    # args: state

    @initial_behavior
    def stateful_beh(self, message):
        print("Have state: {}".format(self.state))
        print("Stateful got message: {}".format(message))


class FlipFlop(Actor):

    @initial_behavior
    def first_beh(self, message):
        print("First: {}".format(message))
        self.behavior = self.second_beh

    def second_beh(self, message):
        print("Second: {}".format(message))
        self.behavior = self.first_beh


class Chain(Actor):

    @initial_behavior
    def chain_beh(self, message):
        if self.count > 0:
            print("Chain: {}".format(self.count))
            next = Chain.create(count=self.count - 1)
            next << message

            
class Echo(Actor):

    @initial_behavior
    def echo_beh(self, message):
        message['reply_to'] << {'answer': message}

        
class Printer(Actor):
    
    @initial_behavior
    def print_beh(self, message):
        print('Got', message)
        

def test():
    stateless = Stateless.create()
    stateless << 'some message'
    stateless << 'more message'

    stateful = Stateful.create(state={'key': 5})
    stateful << {'some': 'other message'}
    stateful << 10

    flipflop = FlipFlop.create()
    flipflop << 'first'
    flipflop << 'second'
    flipflop << 'third'
    flipflop << 'fourth'

    chain = Chain.create(count=10)
    chain << 'go'

    echo = Echo.create()
    printer = Printer.create()
    echo << {'reply_to': printer}


if __name__ == '__main__':
    test()