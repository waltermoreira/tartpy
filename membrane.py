import uuid
from contextlib import contextmanager

from rt import Actor, initial_behavior, Wait
from example import Printer


class Membrane(Actor):
    # args: uid_to_proxy = {uid:actor}, proxy_to_uid = {proxy:uid},
    #       transport = {protocol: tcp|udp|http|...,
    #                    ...data to connect...}

    @initial_behavior
    def start_beh(self, message):
        if message != 'start':
            self.error('membrane is not started yet')
            return
        self.start_server(self.transport)
        self.behavior = self.membrane_beh
        
    def membrane_beh(self, message):
        if 'get_uid' in message:
            actor = message['get_uid']
            uid = self.get_uid(actor)
            message['reply_to']({'uid': uid})
        if 'create_proxy' in message:
            uid = message['create_proxy']
            proxy = self.get_proxy(uid)
            message['reply_to']({'proxy': proxy})
        if '_from' in message:
            proxy = message['_from']
            uid = self.get_uid(proxy)
            msg = self.export_message(message['_original_msg'])
            self.send(to=uid, msg=msg, transport=proxy.transport)
        if '_to' in message:
            rcpt_uid = message['_to']
            msg = self.import_message(message['_msg'])
            proxy = self.get_proxy(rcpt_uid)
            proxy(msg)
            
    def export_message(self, message):
        obj = dict(message)
        for key, value in message.items():
            if isinstance(value, Actor):
                uid = self.get_uid(value)
                obj[key] = {'_proxy': uid,
                            '_transport': self.listeners}
        return obj

    def import_message(self, obj):
        message = dict(obj)
        for key, value in obj.items():
            if isinstance(value, dict) and '_proxy' in value:
                uid = value['_proxy']
                proxy = self.get_proxy(uid)
                proxy.transport = value['_transport']
                message[key] = proxy
        return message
        
    def send(self, to, msg, transport):
        transport_impl = getattr(self, transport['protocol'])
        if transport_impl is None:
            self.error('No transport {0}'.format(transport['protocol']))
            return
        sent = transport_impl(transport, to, msg)
        if not sent:
            self.error('Failed to send message through {0}:\n'
                       '  to: {1}\n'
                       '  msg: {2}\n'
                       '  transport: {3}'.format(transport['protocol'],
                                                 to, msg, transport))

    def get_proxy(self, uid):
        proxy = self.uid_to_proxy.setdefault(uid, Proxy.create(membrane=self))
        self.proxy_to_uid[proxy] = uid
        return proxy
        
    def get_uid(self, actor):
        uid = self.proxy_to_uid.setdefault(actor, uuid.uuid4().hex)
        self.uid_to_proxy[uid] = actor
        return uid
        
    def start_server(self, transport):
        server_impl = getattr(self, '{0}_server'.format(transport['protocol']))
        server_impl(transport)

    def null(self, transport, to, msg):
        self({'_to': to, '_msg': msg})

    def null_server(self, transport):
        pass
        
        
class Proxy(Actor):
    # args: membrane

    @initial_behavior
    def proxy_beh(self, message):
        self.membrane({'_from': self,
                       '_original_msg': message})


def test():
    m = Membrane.create(uid_to_proxy={}, proxy_to_uid={},
                        transport={'protocol': 'null'})
    pr = Printer.create()
    w = Wait.create()
    m('start')
    m({'get_uid': pr,
       'reply_to': w})
    print('uid:', w.act())
    return m
