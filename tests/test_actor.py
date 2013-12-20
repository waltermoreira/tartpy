import pytest
from rt import Actor, initial_behavior

def test_receive_message():
    class A(Actor):
        @initial_behavior
        def receive_beh(self, message):
            assert message == 5

    a = A.create()
    a(5)

def test_create_with_args():
    class A(Actor):
        @initial_behavior
        def receive_beh(self, message):
            assert self.foo == True

    a = A.create(foo=True)
    a(0)


def test_one_shot():

    class OneShot(Actor):
        # args: destination, complete
        
        @initial_behavior
        def one_shot_beh(self, message):
            self.destination(message)
            self.behavior = sink_beh

        def sink_beh(self, message):
            assert message == 'second'
            self.complete('sink_beh_done')

    class Complete(Actor):
        # args: status
        
        @initial_behavior
        def complete_beh(self, message):
            self.status[message] = True
            if self.status.get('sink_beh_done') and self.status.get('one_shot_beh_done'):
                assert True

    class Destination(Actor):
        # args: complete
        
        @initial_behavior
        def destination_beh(self, message):
            assert message == 'first'
            self.complete('destination_beh_done')

    complete = Complete.create(status={})
    destination = Destination.create(complete=complete)
    one_shot = OneShot.create(destination=destination, complete=complete)

    one_shot('first')
    one_shot('second')