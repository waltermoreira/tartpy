from tartpy import eventloop
import pytest
from tartpy.membrane import Membrane, Proxy
from tartpy.rt import Wait

@pytest.fixture(scope='module')
def ev_loop(request):
    loop = eventloop.ThreadedEventLoop.get_loop()
    def shutdown():
        loop.stop()
    request.addfinalizer(shutdown)
    return loop

def test_membrane(ev_loop):
    m1 = Membrane.create()
    m1.transport = {'protocol': 'null',
                    'membrane': m1}
    m2 = Membrane.create()
    m2.transport = {'protocol': 'null',
                    'membrane': m2}
    m1 << 'start'
    m2 << 'start'

    w = Wait.create()
    actor1 = Wait.create()
    actor2 = Wait.create()

    m2 << {'get_uid': actor2,
           'reply_to': w}
    u2 = w.act()['uid']

    m1 << {'create_proxy': u2,
           'transport': {'protocol': 'null',
                         'membrane': m2},
           'reply_to': w}
    proxy_for_2 = w.act()['proxy']
    proxy_for_2 << {'foo': 5,
                    'reply_to': actor1}

    msg = actor2.act()
    assert msg['foo'] == 5

    proxy_for_1 = msg['reply_to']
    assert isinstance(proxy_for_1, Proxy)

    proxy_for_1 << {'bar': 3,
                    'reply_to': actor2}
    msg = actor1.act()
    assert msg['bar'] == 3
    assert msg['reply_to'] is proxy_for_2
    
def test_export(ev_loop):
    m1 = Membrane.create(transport={'protocol': 'null'})
    a = Wait.create()
    obj = m1.export_message({'foo': a})
    assert '_proxy' in obj['foo']
    obj = m1.export_message({'foo': {'bar': a}})
    assert '_proxy' in obj['foo']['bar']