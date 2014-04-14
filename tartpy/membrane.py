"""

Membrane
========

A membrane transparently creates proxies.

"""

import json
import socket
import socketserver
import threading
import uuid
from collections.abc import Mapping, Sequence

from logbook import Logger

from .runtime import behavior, Actor, exception_message
from .tools import actor_map

logger = Logger('membrane')


class MembraneFactory(object):
    
    def __init__(self):
        self.proxy_to_actor = {}
        self.actor_to_proxy = {}
        
    @behavior
    def membrane_beh(self, this, message):
        tag = message.get('tag', 'error')
        getattr(self, tag)(this, message)

    def _create_proxy(self, this, actor):
        if actor in self.actor_to_proxy:
            return self.actor_to_proxy[actor]
        proxy = this.create(self.proxy_beh, actor)
        self.proxy_to_actor[proxy] = actor
        self.actor_to_proxy[actor] = proxy
        return proxy

    def _is_proxy(self, actor):
        return actor in self.proxy_to_actor
        
    def create_proxy(self, this, message):
        """Create proxy for an actor.

        `message` has the form::

            {'tag': 'create_proxy',
             'actor': ...,
             'customer': ...
            }

        """
        actor = message['actor']
        proxy = self._create_proxy(this, actor)
        message['customer'] << proxy
        
    @behavior
    def proxy_beh(self, actor, this, message):
        actor << self.convert(this, message)

    def convert(self, this, message):
        def f(actor):
            return (actor
                    if self._is_proxy(actor)
                    else self._create_proxy(this, actor))
        return actor_map(f, message)


def test():
    from .runtime import Runtime
    from .example import print_beh, echo_beh
    from .tools import Wait
    
    runtime = Runtime()

    membrane_inst = MembraneFactory()
    membrane = runtime.create(membrane_inst.membrane_beh)
    printer = runtime.create(print_beh)
    print('printer:', printer)
    
    @behavior
    def print_echo_beh(self, msg):
        print('echo got', msg)
        msg['customer'] << {'answer': msg}

    print_echo = runtime.create(print_echo_beh)
    print('print_echo:', print_echo)

    w = Wait()
    wait = runtime.create(w.wait_beh)

    membrane << {'tag': 'create_proxy',
                 'actor': print_echo,
                 'customer': wait}
    proxy = w.join()
    proxy << {'customer': printer}
    
    return membrane_inst

    
