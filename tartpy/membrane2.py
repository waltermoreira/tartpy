import uuid

from collections.abc import Mapping, Sequence
from logbook import Logger
from .runtime import behavior, Actor


logger = Logger('membrane2')


class Membrane(object):
    
    def __init__(self, config, runtime):
        self.config = config
        if self.config['protocol'] == 'membrane':
            self.config['target'] = self
        self.runtime = runtime
        self.uid_to_proxy = {}
        self.proxy_to_uid = {}
        self.start_server()

    def get_proxy(self, uid):
        """Get proxy associated to ``uid``.

        Raise an exception is there is not associated proxy.

        """
        proxy = self.uid_to_proxy[uid]
        self.proxy_to_uid[proxy] = uid
        return proxy

    def create_proxy(self, uid, remote):
        """Create proxy for ``uid`` in the ``remote`` membrane."""
        proxy = self.runtime.create(self.proxy, uid, remote)
        self.uid_to_proxy[uid] = proxy
        self.proxy_to_uid[proxy] = uid
        return proxy

    def get_or_create_proxy(self, uid, remote):
        """Get or create a new proxy for ``uid`` in the ``remote`` membrane."""
        try:
            return self.get_proxy(uid)
        except KeyError:
            return self.create_proxy(uid, remote)
            
    def get_uid(self, actor):
        """Convert an actor to a uid."""
        uid = self.proxy_to_uid.setdefault(actor, uuid.uuid4().hex)
        self.uid_to_proxy[uid] = actor
        return uid

    @behavior
    def proxy(self, uid, remote, this, msg):
        protocol = remote['protocol']
        client = getattr(self, '{}_client'.format(protocol))
        client(self.export(msg), uid, remote)

    def local_delivery(self, uid, msg):
        """Deliver ``msg`` to actor with id ``uid``."""
        self.uid_to_proxy[uid] << msg

    def export(self, msg):
        """Export a message.

        Convert any actor reference to a uid. Proceed recursively to
        convert references at any level.

        """
        if isinstance(msg, Actor):
            uid = self.get_uid(msg)
            return {'_proxy': uid,
                    '_config': self.config}
        if isinstance(msg, Mapping):
            return {key:self.export(value)
                    for key, value in msg.items()}
        if isinstance(msg, str):
            return msg
        if isinstance(msg, Sequence):
            return [self.export(value) for value in msg]
        return msg

    def start_server(self):
        pass
    
    def membrane_client(self, msg, uid, remote):
        logger.debug('membrane client')
        logger.debug(' target: uid: %s' %uid)
        logger.debug(' at membrane: %s' %remote['target'])
        logger.debug(' and message is %s' %msg)

        remote['target'].local_delivery(uid, msg)

def test():
    from .runtime import SimpleRuntime
    from .example import print_beh
    from .eventloop import EventLoop

    runtime = SimpleRuntime()

    mb = Membrane({'protocol': 'membrane'}, runtime)
    printer = runtime.create(print_beh)
    uid_at_mb = mb.get_uid(printer)

    mb2 = Membrane({'protocol': 'membrane'}, runtime)
    proxy2 = mb2.create_proxy(uid_at_mb, {'protocol': 'membrane',
                                          'target': mb})
    
    evloop = EventLoop()
    
    return locals()