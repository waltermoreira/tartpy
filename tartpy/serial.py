from .behavior import behavior, runtime

@behavior
def serial_beh(actors, ctx, msg):
    if actors:
        tail = ctx.create(serial_beh, actors[1:])
        msg['reply_to'] = tail
        actors[0] << msg

@behavior
def add_beh(ctx, msg):
    cust = msg['reply_to']
    msg['x'] += 1
    cust << msg

@behavior
def print_beh(ctx, msg):
    print('got:', msg)
    
def test():
    pr = runtime.create(print_beh)
    a = runtime.create(add_beh)
    b = runtime.create(add_beh)

    x = runtime.create(serial_beh, [a, b, pr])
    x << {'x': 0}