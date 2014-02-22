import pytest

from tartpy.rt import ActorManualLoop, ActorOwnManualLoop, initial_behavior
from tartpy.sponsor import SimpleSponsor

    
def test_receive_message():
    
    class A(ActorManualLoop):
        @initial_behavior
        def receive_beh(self, message):
            self.message = message

    a = A.create()
    a(5)
    a.loop.run()
    assert a.message == 5

    
def test_create_with_args():
    
    class A(ActorManualLoop):
        @initial_behavior
        def receive_beh(self, message):
            self.arg = self.foo

    a = A.create(foo=True)
    a(0)
    a.loop.run()
    assert a.arg is True

def test_one_shot():

    class OneShot(ActorManualLoop):
        # args: destination
        
        @initial_behavior
        def one_shot_beh(self, message):
            self.destination(message)
            self.behavior = self.sink_beh

        def sink_beh(self, message):
            assert message == 'second'
            self.sink_beh_done = True

    class Destination(ActorManualLoop):
        
        @initial_behavior
        def destination_beh(self, message):
            self.msg = message
            self.destination_beh_done = True

    destination = Destination.create()
    one_shot = OneShot.create(destination=destination)

    one_shot('first')
    one_shot('second')

    one_shot.loop.run()
    assert destination.msg == 'first'
    assert one_shot.sink_beh_done and destination.destination_beh_done
    
def test_serial():

    class Serial(ActorManualLoop):
        # args: first, second, third

        def record(self):
            return (bool(self.first), bool(self.second), bool(self.third))
            
        @initial_behavior
        def first_beh(self, msg):
            self.behavior = self.second_beh
            self.first_msg = msg
            self.first_behavior = self.record()
            self.first = True

        def second_beh(self, msg):
            self.behavior = self.third_beh
            self.second_msg = msg
            self.second_behavior = self.record()
            self.second = True

        def third_beh(self, msg):
            self.third_msg = msg
            self.third_behavior = self.record()

    serial = Serial.create(first=False, second=False, third=False)
    serial('foo')
    serial('foo')
    serial('foo')

    serial.loop.run()
    assert serial.first_msg == 'foo' and serial.second_msg == 'foo' and serial.third_msg == 'foo'
    assert serial.first_behavior == (False, False, False)
    assert serial.second_behavior == (True, False, False)
    assert serial.third_behavior == (True, True, False)

def test_simple_sponsor():

    class A(ActorManualLoop):
        @initial_behavior
        def beh(self, message):
            pass

    sponsor = SimpleSponsor()
    a = A.create(key=1, sponsor=sponsor)
    assert sponsor.actors.qsize() == 1
    assert sponsor.actors.get() == (A, {'key': 1, 'sponsor': sponsor})
    assert a.sponsor == sponsor

def test_setup():

    class A(ActorOwnManualLoop):

        def setup(self):
            self.foo = 5

        @initial_behavior
        def beh(self, message):
            return self.foo

    a = A.create()
    a(0)
    x = a.act()
    assert x == 5
    
    b = A.create(foo=3)
    b(0)
    y = b.act()
    assert y == 3