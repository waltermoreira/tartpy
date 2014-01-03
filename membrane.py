import uuid
from contextlib import contextmanager

from rt import Actor, initial_behavior
from example import Printer


class AbstractMembrane(Actor):
    # args: uid_to_proxy = {uid:actor}, proxy_to_uid = {proxy:uid}

    @initial_behavior
    def membrane_beh(self, message):
        if '_create_proxy' in message:
            uid = message['_create_proxy']
            proxy = self.get_proxy(uid)
            message['reply_to']({'proxy': proxy})
        if '_from' in message:
            proxy = message['_from']
            uid = self.get_uid(proxy)
            msg = self.export_message(message['_original_msg'])
            self.send(to=uid, msg=msg)

    def export_message(self, message):
        obj = dict(message)
        for key, value in message.items():
            if isinstance(value, Actor):
                uid = self.get_uid(value)
                obj[key] = {'_proxy': uid}
        return obj

    def import_message(self, obj):
        message = dict(obj)
        for key, value in obj.items():
            if isinstance(value, dict) and '_proxy' in value:
                uid = value['_proxy']
                proxy = self.get_proxy(uid)
                message[key] = proxy
        return message
        
    def send(self, to, msg):
        pass

    def receive(self, wrapped):
        pass

    def get_proxy(self, uid):
        proxy = self.uid_to_proxy.setdefault(uid, Proxy.create(membrane=self))
        self.proxy_to_uid[proxy] = uid
        return proxy
        
    def get_uid(self, actor):
        uid = self.proxy_to_uid.setdefault(actor, uuid.uuid4().hex)
        self.uid_to_proxy[uid] = actor
        return uid

        
class Proxy(Actor):
    # args: membrane

    @initial_behavior
    def proxy_beh(self, message):
        self.membrane({'_from': self,
                       '_original_msg': message})


def test():
    pr = Printer.create()
    m = AbstractMembrane.create(uid_to_proxy={}, proxy_to_uid={})
    m({'_create_proxy': 10, 'reply_to': pr})
    return m, pr