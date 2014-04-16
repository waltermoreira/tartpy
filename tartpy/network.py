from collections.abc import Mapping, Sequence
import json
import socket
import socketserver
import threading
from urllib.parse import urlparse
import uuid

from logbook import Logger

from .runtime import Runtime, behavior, Actor
from .tools import actor_map, dict_map


logger = Logger('network')


class NetworkRuntime(Runtime):

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.uid_to_actor = {}
        self.actor_to_uid = {}

        self.server_type = {'tcp': TCPServer}
        self.server = self.network_server()
        self.server.start()

        self.client_type = {'tcp': TCPClient}
        self.clients = {}

    def uid_for_actor(self, actor):
        uid = self.actor_to_uid.setdefault(actor, uuid.uuid4().hex)
        self.uid_to_actor[uid] = actor
        return uid

    def actor_for_uid(self, remote_url, uid):
        proxy = self.uid_to_actor.setdefault(uid,
                                             self.create(self.proxy_beh,
                                                         remote_url, uid))
        self.uid_to_actor[uid] = proxy
        self.actor_to_uid[proxy] = uid
        return proxy

    def marshall_actor(self, actor):
        uid = self.uid_for_actor(actor)
        return {'_url': self.url,
                '_uid': uid}

    def marshall(self, message):
        return actor_map(self.marshall_actor, message)

    def unmarshall_actor(self, msg):
        return self.actor_for_uid(msg['_url'], msg['_uid'])

    def unmarshall(self, message):
        def primitive(x):
            return (isinstance(x, Mapping) and
                    set(x.keys()) == {'_uid', '_url'})
        return dict_map(self.unmarshall_actor, primitive, message)
        
    @behavior
    def proxy_beh(self, remote_url, uid, this, message):
        msg = self.marshall(message)
        self.network_send(remote_url, uid, msg)

    def network_send(self, remote_url, uid, msg, retry=2):
        client = self.network_client(remote_url)
        try:
            client.send({'_to': uid,
                         '_msg': msg})
            return
        except OSError as e:
            if retry == 2:
                client.connect()
                self.network_send(remote_url, uid, msg, retry=1)
            elif retry == 1:
                del self.clients[remote_url]
                self.network_send(remote_url, uid, msg, retry=0)
            else:
                self.throw('client failed to send to {}'.format(remote_url))

    def network_client(self, url):
        try:
            return self.clients[url]
        except KeyError:
            client = self.choose_for_scheme(url, self.client_type)(self, url)
            self.clients[url] = client
            return client

    def network_server(self):
        return self.choose_for_scheme(self.url, self.server_type)(self)

    def choose_for_scheme(self, url, dic):
        scheme = urlparse(url).scheme
        try:
            return dic[scheme]
        except KeyError:
            self.throw({'error': "no client/server for scheme '{}'"
                        .format(scheme)})
        

class AbstractClient(object):

    def __init__(self, runtime, url):
        self.runtime = runtime
        self.url = url

    def connect(self):
        pass

    def send(self, message):
        pass

        
class TCPClient(AbstractClient):

    def __init__(self, runtime, url):
        super().__init__(runtime, url)
        parsed = urlparse(url)
        self.host = parsed.hostname
        self.port = parsed.port
        self.connect()

    def connect(self):
        self.socket = socket.socket()
        self.socket.connect((self.host, self.port))
        self.socket_file = self.socket.makefile('w', encoding='utf-8')

    def send(self, message):
        self.socket_file.write(json.dumps(message) + '\n')
        self.socket_file.flush()
        
        
class AbstractServer(object):

    def __init__(self, runtime):
        self.runtime = runtime

    def start(self):
        pass

    def receive_message(self, message):
        pass


class TCPServer(AbstractServer):

    def __init__(self, runtime):
        super().__init__(runtime)
        parsed = urlparse(self.runtime.url)
        self.host = parsed.hostname
        self.port = parsed.port
        
    def start(self):
        class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
            allow_reuse_address = True
 
        class ThreadedTCPHandler(socketserver.StreamRequestHandler):
            def handle(this):
                while True:
                    s = this.rfile.readline().decode('utf-8')
                    if not s:
                        return
                    wrapped_msg = json.loads(s)
                    self.receive_message(wrapped_msg)

        server = ThreadedTCPServer((self.host, self.port), ThreadedTCPHandler)
        server_thread = threading.Thread(target=server.serve_forever,
                                         name='tcp_server')
        server_thread.daemon = True
        server_thread.start()

    def receive_message(self, message):
        uid = message['_to']
        msg = message['_msg']
        target = self.runtime.actor_for_uid(self.runtime.url, uid)
        target << self.runtime.unmarshall(msg)




def test(port):
    from .tools import log_beh
    
    network_runtime = NetworkRuntime('tcp://localhost:{}'.format(port))
    runtime = network_runtime
    log = runtime.create(log_beh)

    uid = runtime.uid_for_actor(log)
    proxy = runtime.create(runtime.proxy_beh, runtime.url, uid)
    
    return locals()
    