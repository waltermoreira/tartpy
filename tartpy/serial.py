from .runtime import behavior

@behavior
def serial_beh(actors, self, msg):
    if actors:
        tail = self.create(serial_beh, actors[1:])
        msg['reply_to'] = tail
        actors[0] << msg

@behavior
def add_beh(self, msg):
    cust = msg['reply_to']
    msg['x'] += 1
    cust << msg

@behavior
def print_beh(self, msg):
    print('got:', msg)
    
def test():
    from .runtime import SimpleRuntime
    from .eventloop import EventLoop
    
    runtime = SimpleRuntime()

    pr = runtime.create(print_beh)
    a = runtime.create(add_beh)
    b = runtime.create(add_beh)

    x = runtime.create(serial_beh, [a, b, pr])
    x << {'x': 0}

    EventLoop().run()