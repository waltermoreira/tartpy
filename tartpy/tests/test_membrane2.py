import pytest

from tartpy.runtime import SimpleRuntime, behavior
from tartpy.eventloop import EventLoop
from tartpy.membrane2 import Membrane


def test_membrane_protocol():
    runtime = SimpleRuntime()
    evloop = EventLoop()
    
    m1 = Membrane({'protocol': 'membrane'}, runtime)
    m2 = Membrane({'protocol': 'membrane'}, runtime)

    result1 = None
    @behavior
    def actor1_beh(self, msg):
        nonlocal result1
        result1 = msg

    result2 = None
    @behavior
    def actor2_beh(self, msg):
        nonlocal result2
        result2 = msg

    actor1 = runtime.create(actor1_beh)
    actor2 = runtime.create(actor2_beh)

    uid_for_2_at_mb2 = m2.get_uid(actor2)
    proxy_for_2_at_mb1 = m1.create_proxy(uid_for_2_at_mb2,
                                         m2.config)
    
    proxy_for_2_at_mb1 << {'foo': 5,
                           'reply_to': actor1}
    
    evloop.run()

    # test message from m1 to m2
    assert result2['foo'] == 5

    # test that 'reply_to' is a proxy at m2
    proxy_for_1_at_mb2 = result2['reply_to']
    assert proxy_for_1_at_mb2 is not actor1

    proxy_for_1_at_mb2 << {'bar': 3,
                           'reply_to': actor2}

    evloop.run()

    # test message back from m2 to m1
    assert result1['bar'] == 3

    # test that proxy at m1 is reused
    assert result1['reply_to'] is proxy_for_2_at_mb1

    # test a string message across Membranes
    proxy_for_2_at_mb1 << 'a string message'
    evloop.run()
    assert result2 == 'a string message'

def test_dos():
    runtime = SimpleRuntime()
    m = Membrane({'protocol': 'membrane'}, runtime)
    with pytest.raises(KeyError):
        m.local_delivery(0, {})

def test_marshall_unmarshall():
    runtime = SimpleRuntime()
    m = Membrane({'protocol': 'membrane'}, runtime)

    assert m.marshall_message(5) == 5
    assert m.marshall_message('foo') == 'foo'
    assert m.marshall_message([1, 2, 'bar']) == [1, 2, 'bar']
    assert m.marshall_message({'foo': 5, 'bar': 'baz'}) == {'foo': 5, 'bar': 'baz'}

    assert m.unmarshall_message(5) == 5
    assert m.unmarshall_message('foo') == 'foo'
    assert m.unmarshall_message([1, 2, 'bar']) == [1, 2, 'bar']
    assert m.unmarshall_message({'foo': 5, 'bar': 'baz'}) == {'foo': 5, 'bar': 'baz'}

    @behavior
    def sink_beh(self, msg):
        pass
    sink = runtime.create(sink_beh)
    
    s = m.marshall_message(sink)
    assert m.is_marshalled_actor(s)
    assert m.unmarshall_message(s) is sink

    s = m.marshall_message({'foo': sink})
    assert m.is_marshalled_actor(s['foo'])
    assert m.unmarshall_message(s)['foo'] is sink

    s = m.marshall_message([sink])
    assert m.is_marshalled_actor(s[0])
    assert m.unmarshall_message(s)[0] is sink


