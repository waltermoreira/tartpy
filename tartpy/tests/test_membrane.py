from collections.abc import Mapping

import pytest

from tartpy.runtime import SimpleRuntime, behavior
from tartpy.eventloop import EventLoop
from tartpy.membrane import MembraneFactory

def test_membrane_protocol():
    runtime = SimpleRuntime()
    evloop = EventLoop()

    membrane_inst = MembraneFactory()
    membrane = runtime.create(membrane_inst.membrane_beh)

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

    actor2_proxy = None
    @behavior
    def go_beh(self, msg):
        nonlocal actor2_proxy
        if msg == 'go':
            membrane << {'tag': 'create_proxy',
                         'actor': actor2,
                         'customer': self}
        else:
            actor2_proxy = msg

    go = runtime.create(go_beh)
    go << 'go'

    evloop.run()

    actor2_proxy << {'foo': 5,
                     'customer': actor1}

    evloop.run()

    # test message from actor1 to actor2
    assert result2['foo'] == 5

    # test that customer is really a proxy
    assert result2['customer'] is not actor1

    actor1_proxy = result2['customer']
    actor1_proxy << {'bar': 3,
                     'customer': actor2}

    evloop.run()

    # test message from actor2 to actor1
    assert result1['bar'] == 3

    # test that proxy of actor2 is reused
    assert result1['customer'] is actor2_proxy

    # test a string message
    actor2_proxy << 'a string message'
    evloop.run()
    assert result2 == 'a string message'

