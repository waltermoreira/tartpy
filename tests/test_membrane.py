from membrane import Membrane, Proxy
from rt import Wait

def test_membrane():
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
    proxy = w.act()['proxy']
    proxy << {'foo': 5,
              'reply_to': actor1}

    msg = actor2.act()
    assert msg['foo'] == 5

    proxy2 = msg['reply_to']
    assert isinstance(proxy2, Proxy)

    proxy2 << {'bar': 3,
               'reply_to': actor2}
    msg = actor1.act()
    assert msg['bar'] == 3
    assert msg['reply_to'] is proxy
    
def test_export():
    m1 = Membrane.create(transport={'protocol': 'null'})
    a = Wait.create()
    obj = m1.export_message({'foo': a})
    assert '_proxy' in obj['foo']
    obj = m1.export_message({'foo': {'bar': a}})
    assert '_proxy' in obj['foo']['bar']