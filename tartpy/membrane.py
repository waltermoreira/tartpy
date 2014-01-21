"""

Membrane
========

A membrane moves messages between configurations of actors.  The
membrane creates proxy objects for actors on each side, and it forward
messages from the proxy to the associated actor.

Membranes deliver and receive messages using network protocols.  A
simple empty protocol is provided for communicating two membranes in
the same process.


"""

from contextlib import contextmanager
import json
import uuid
import socket
import socketserver
import threading

from .example import Printer, Echo
from .rt import AbstractActor, Actor, initial_behavior, Wait


class Membrane(Actor):
    # args: transport = {protocol: tcp|udp|http|...,
    #                    ...data to connect...}

    def setup(self):
        self.uid_to_proxy = {}  # {uid: actor}
        self.proxy_to_uid = {}  # {proxy: uid}
        
    @initial_behavior
    def start_beh(self, message):
        """Accept a 'start' message.

        Start the server necessary for other membranes to communicate
        with this one.

        Change behavior for standard membrane duties.

        """
        if message != 'start':
            self.error('membrane is not started yet')
            return
        self.start_server(self.transport)
        self.behavior = self.membrane_beh
        
    def membrane_beh(self, message):
        """Membrane behavior.

        It accepts the following messages:

        - ``{get_uid: actor, reply_to: customer}``: get uid for an
           actor. The uid can be distributed for other membranes to
           construct proxies for ``actor``.

        - ``{create_proxy: uid, transport: {...}, reply_to:
          customer}``: create a proxy for a given uid and transport.

        - ``{_from: actor, _msg: msg}``: forward (export) the message
           ``msg`` from the proxy ``actor`` to the proper membrane.

        - ``{_to: uid, _msg: msg}``: import the message ``msg`` from
           the outside into the actor with identifier ``uid``.

        """
        if 'get_uid' in message:
            actor = message['get_uid']
            uid = self.get_uid(actor)
            message['reply_to']({'uid': uid})
        if 'create_proxy' in message:
            uid = message['create_proxy']
            proxy = self.create_proxy(uid)
            proxy.transport = message.get('transport', {'protocol': 'null',
                                                        'membrane': self})
            message['reply_to']({'proxy': proxy})
        if '_from' in message:
            proxy = message['_from']
            uid = self.get_uid(proxy)
            msg = self.export_message(message['_msg'])
            to_export = {'_to': uid, '_msg': msg}
            self.send(to_export, transport=proxy.transport)
        if '_to' in message:
            rcpt_uid = message['_to']
            msg = self.import_message(message['_msg'])
            proxy = self.get_proxy(rcpt_uid)
            proxy(msg)
            
    def export_message(self, message):
        """Export a message.

        Convert any actor reference to a uid. Proceed recursively to
        convert references at any level.

        """
        obj = {}
        for key, value in message.items():
            if isinstance(value, AbstractActor):
                uid = self.get_uid(value)
                new_value = {'_proxy': uid,
                             '_transport': self.transport}
            elif isinstance(value, dict):
                new_value = self.export_message(value)
            else:
                new_value = value
            obj[key] = new_value
        return obj

    def import_message(self, obj):
        """Import a message.

        Uid identifiers of the form::

            {'_proxy': uid,
             '_transport': ...}

        are substituted for the proper actor to which they refer.

        """
        message = dict(obj)
        for key, value in obj.items():
            if isinstance(value, dict) and '_proxy' in value:
                uid = value['_proxy']
                proxy = self.get_or_create_proxy(uid)
                proxy.transport = value['_transport']
                message[key] = proxy
        return message
        
    def send(self, msg, transport):
        """Send a message to an external membrane.

        Deliver the message ``msg`` directed to uid ``to``, using the
        transport information in ``transport``.

        """
        transport_impl = getattr(self, '{0}_client'.format(transport['protocol']))
        if transport_impl is None:
            self.error('No transport {0}'.format(transport['protocol']))
            return
        sent = transport_impl(msg, transport)
        if not sent:
            self.error('Failed to send message through {0}:\n'
                       '  msg: {1}\n'
                       '  transport: {2}'.format(transport['protocol'],
                                                 msg, transport))

    def get_proxy(self, uid):
        """Convert an uid to an actor."""
        proxy = self.uid_to_proxy[uid]
        self.proxy_to_uid[proxy] = uid
        return proxy

    def create_proxy(self, uid):
        proxy = Proxy.create(membrane=self)
        self.uid_to_proxy[uid] = proxy
        self.proxy_to_uid[proxy] = uid
        return proxy

    def get_or_create_proxy(self, uid):
        try:
            return self.get_proxy(uid)
        except KeyError:
            return self.create_proxy(uid)
            
    def get_uid(self, actor):
        """Convert an actor to a uid."""
        uid = self.proxy_to_uid.setdefault(actor, uuid.uuid4().hex)
        self.uid_to_proxy[uid] = actor
        return uid
        
    def start_server(self, transport):
        """Start server for the given transport.

        To implement a transport ``X``, implement the methods:

        - ``X_server(transport)``: start a listener for protocol
          ``X``, using information contained in the dictionary
          ``transport``.

        - ``X_client(msg, transport)``: send message ``msg``, using
          transport information for protocol X in the dictionary
          ``transport``.

        """
        server_impl = getattr(self, '{0}_server'.format(transport['protocol']))
        server_impl(transport)

    def null_client(self, msg, transport):
        """Deliver directly to a membrane.

        Send message directly to the actor referenced by
        ``transport['membrane']``.

        """
        target_membrane = transport['membrane']
        target_membrane(msg)
        return True

    def null_server(self, transport):
        """Null server.

        Basic protocol to send membrane to membrane inside the same
        process.  Data for connection has the form::

            {'transport': 'null',
             'membrane': membrane}

        """
        pass

    def tcp_client(self, msg, transport):
        """Client for tcp transport.

        Send message as a JSON object with UTF-8 encoding.

        """
        ip = transport['ip']
        port = transport['port']
        sock = socket.socket()
        sock.connect((ip, port))
        sock_file = sock.makefile('w', encoding='utf8')
        try:
            sock_file.write(json.dumps(msg) + '\n')
        finally:
            sock_file.close()
            sock.close()
        return True

    def tcp_server(self, transport):
        """Server for tcp transport.

        Use a threaded stream server from the standard library.

        """
        class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
            allow_reuse_address = True

        membrane = self
        class ThreadedTCPHandler(socketserver.StreamRequestHandler):
            def handle(self):
                s = self.rfile.readline().decode('utf-8')
                if s:
                    obj = json.loads(s)
                    membrane << obj

        ip = transport['ip']
        port = transport['port']
        server = ThreadedTCPServer((ip, port), ThreadedTCPHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

    @classmethod
    def add_transport(cls, name, client, server):
        """Dynamically add a new transport with name ``name``.

        Implement two functions with signature:

        - ``{name}_server(transport)``
        - ``{name}_client(msg, transport)``

        See ``start_server`` for details.

        """
        setattr(cls, '{0}_client'.format(name), client)
        setattr(cls, '{0}_server'.format(name), server)

        
class Proxy(Actor):
    """A proxy actor.

    A proxy forwards any message to its associated membrane, adding
    also the information of itself so the membrane can locate its
    uid.

    """

    # args: membrane

    @initial_behavior
    def proxy_beh(self, message):
        self.membrane({'_from': self,
                       '_msg': message})


def test():
    m1 = Membrane.create(transport={'protocol': 'tcp',
                                    'ip': 'localhost',
                                    'port': 5555})
    m2 = Membrane.create(transport={'protocol': 'tcp',
                                    'ip': 'localhost',
                                    'port': 6666})
    m1 << 'start'
    m2 << 'start'

    actor2 = Echo.create()
    actor1 = Printer.create()

    w = Wait.create()
    m2 << {'get_uid': actor2,
           'reply_to': w}
    u2 = w.act()['uid']

    m1 << {'create_proxy': u2,
           'transport': {'protocol': 'tcp',
                         'ip': 'localhost',
                         'port': 6666},
           'reply_to': w}
    proxy = w.act()['proxy']

    proxy << {'foo': 3,
              'reply_to': actor1}

    return m1, m2