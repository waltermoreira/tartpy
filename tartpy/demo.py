from tartpy.runtime import Runtime, behavior

runtime = Runtime()


@behavior
def demo_beh(self, message):
    print(message)

demo_actor = runtime.create(demo_beh)


@behavior
def counter_beh(state, self, message):
    print('Start count:', state['count'])
    print('Message:    ', message)

    state['count'] += message

    print('End count:  ', state['count'])

counter = runtime.create(counter_beh, {'count': 1337})


@behavior
def ping_beh(self, message):
    print('[PING****] send')
    message << self
    print('[PING****] finish')

@behavior
def pong_beh(state, self, message):
    if state['count'] == 0:
        print('[****PONG] Done')
        return

    print('[****PONG] send')
    message << self
    print('[****PONG] finish')
    state['count'] -= 1

ping = runtime.create(ping_beh)
pong = runtime.create(pong_beh, {'count': 2})

ping << pong


@behavior
def show_self_beh(self, message):
    print(self)
    print(dir(self))

show_self = runtime.create(show_self_beh)
show_self << None


@behavior
def say_red_beh(self, message):
    print('[SAYING]: red')
    self.become(say_black_beh)

@behavior
def say_black_beh(self, message):
    print('[SAYING]: black')
    self.become(say_red_beh)

say = runtime.create(say_red_beh)
say << None


@behavior
def flip_up_beh(state, self, message):
    print(state, 'flipping up...')
    self.become(flip_down_beh, 'up')

@behavior
def flip_down_beh(state, self, message):
    print(state, 'flipping down...')
    self.become(flip_up_beh, 'down')

flipper = runtime.create(flip_down_beh, 'neither')


