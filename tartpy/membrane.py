"""

Membrane
========

A membrane moves messages between configurations of actors.  The
membrane creates proxy objects for actors before deliverying the
message to another membrane.
 
Membranes deliver and receive messages using arbitrary protocols.  A
simple "membrane to membrane"" protocol is provided for communicating
two membranes in the same process. Other protocols can be added by
implementing a server and a client.

"""

import json
import socket
import socketserver
import threading
import uuid
from collections.abc import Mapping, Sequence

from logbook import Logger

from .runtime import behavior, Actor


logger = Logger('membrane')


class Membrane(object):
    """A membrane object.

    Create a membrane with `Membrane(config, runtime)`.  `config` is a
    dictionary of the form::

        {'protocol': '...',
         ...data to connect...}

    """
    
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
        """Behavior for a proxy.

        This actor represents an actor with id `uid` in the membrane
        `remote`.

        `remote` is the config information to reach the remote
        membrane.

        """
        protocol = remote['protocol']
        client = getattr(self, '{}_client'.format(protocol))
        client(self.marshall_message(msg), uid, remote)

    def start_server(self):
        protocol = self.config['protocol']
        server = getattr(self, '{}_server'.format(protocol))
        server()
    
    def local_delivery(self, uid, msg):
        """Deliver ``msg`` to actor with id ``uid``."""
        self.uid_to_proxy[uid] << self.unmarshall_message(msg)

    def marshall_actor(self, actor):
        """Convert an actor to a JSON object.

        Include information to reach back the local membrane.

        """
        uid = self.get_uid(actor)
        return {'_proxy': uid,
                '_config': self.config}

    def unmarshall_actor(self, obj):
        """Convert a JSON object to a proxy actor."""
        uid = obj['_proxy']
        return self.get_or_create_proxy(uid, obj['_config'])

    def is_marshalled_actor(self, obj):
        """Decide if a JSON object has the form of a marshalled actor."""
        try:
            return set(obj.keys()) == {'_proxy', '_config'}
        except AttributeError:
            return False
        
    def unmarshall_message(self, msg):
        """Import a message.

        Uid identifiers of the form::

            {'_proxy': uid,
             '_transport': ...}

        are substituted for the proper actor to which they refer.

        """
        if self.is_marshalled_actor(msg):
            return self.unmarshall_actor(msg)
        if isinstance(msg, Mapping):
            return {key:self.unmarshall_message(value)
                    for key, value in msg.items()}
        if isinstance(msg, str):
            return msg
        if isinstance(msg, Sequence):
            return [self.unmarshall_message(value) for value in msg]
        return msg
            
    def marshall_message(self, msg):
        """Export a message.

        Convert any actor reference to a uid. Proceed recursively to
        convert references at any level.

        """
        if isinstance(msg, Actor):
            return self.marshall_actor(msg)
        if isinstance(msg, Mapping):
            return {key:self.marshall_message(value)
                    for key, value in msg.items()}
        if isinstance(msg, str):
            return msg
        if isinstance(msg, Sequence):
            return [self.marshall_message(value) for value in msg]
        return msg

    def membrane_client(self, msg, uid, remote):
        logger.debug('membrane client')
        logger.debug(' target: uid: %s' %uid)
        logger.debug(' at membrane: %s' %remote['target'])
        logger.debug(' and message is %s' %msg)

        remote['target'].local_delivery(uid, msg)
        return True

    def membrane_server(self):
        pass

    def tcp_client(self, msg, uid, remote):
        """Client for socket connections.

        `remote` has the form::

            {'protocol': 'tcp',
             'ip': '127.0.0.1',
             'port': 1234}
        """
        ip = remote['ip']
        port = remote['port']
        sock = socket.socket()
        wrapped_msg = {'to': uid,
                       'msg': msg}
        sock.connect((ip, port))
        sock_file = sock.makefile('w', encoding='utf8')
        try:
            sock_file.write(json.dumps(wrapped_msg) + '\n')
        finally:
            sock_file.close()
            sock.close()
        return True

    def tcp_server(self):
        """Server for tcp connections.
 
        Use a threaded stream server from the standard library.
 
        """
        class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
            allow_reuse_address = True
 
        membrane = self
        class ThreadedTCPHandler(socketserver.StreamRequestHandler):
            def handle(self):
                s = self.rfile.readline().decode('utf-8')
                if s:
                    wrapped_msg = json.loads(s)
                    uid = wrapped_msg['to']
                    msg = wrapped_msg['msg']
                    membrane.local_delivery(uid, msg)
 
        ip = self.config['ip']
        port = self.config['port']
        server = ThreadedTCPServer((ip, port), ThreadedTCPHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        

def test():
    from .runtime import SimpleRuntime
    from .example import print_beh, echo_beh
    from .eventloop import EventLoop

    runtime = SimpleRuntime()

    @behavior
    def print_echo_beh(self, msg):
        print('echo got', msg)
        msg['reply_to'] << {'answer': msg}
        
    mb = Membrane({'protocol': 'membrane'}, runtime)
    print_echo = runtime.create(print_echo_beh)
    uid_at_mb = mb.get_uid(print_echo)

    mb2 = Membrane({'protocol': 'membrane'}, runtime)
    proxy_for_echo = mb2.create_proxy(uid_at_mb, {'protocol': 'membrane',
                                                  'target': mb})
    printer = runtime.create(print_beh)
    proxy_for_echo << {'tag': 5, 'reply_to': printer}
    
    evloop = EventLoop()
    
    return locals()