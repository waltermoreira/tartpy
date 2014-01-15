"""

Base classes for actors
=======================

Actors subclass from ``AbstractActor`` and mostly implement the way to
dispatch messages.

In general, an actor is declared as::

    class Foo(Actor):

        def setup(self):
            # set initial state variables, if necessary

        @initial_behavior
        def foo_beh(self, message):
            ...

        def bar_beh(self, message):
            ...

The method decorated with ``initial_behavior`` is the default behavior
for the actor.  The actor can change behaviors (*become* operator)
with::

    self.behavior = self.bar_beh

Actors are created from the declaration with::

    foo = Foo.create(arg1=val1, arg2=val2, ...)

where ``arg1``, ``arg2``, etc. are keyword arguments that can be
accesed inside the actor via ``self.arg1``, ``self.arg2``, etc.

Messages to the actor ``foo`` are sent with::

    foo(arbitrary_message)


Exports
-------

- ``ActorOwnLoop``: actor with independent event loop

- ``ActorGlobalLoop``: actor using a global event loop

- ``ActorManualLoop``: actor using a global event loop, that
                       can be run step-wise

- ``ActorOwnManualLoop``: actor with a full step-wise loop

- ``Wait``: actor that waits (and blocks) for messages

- ``initial_behavior``: decorator for actor entry point

"""


import pprint
import queue
import threading

from . import eventloop


def initial_behavior(f):
    """Decorator to specify the entry point of an actor."""
    f.initial_behavior = True
    return f
        

class MetaActor(type):
    """Metaclass of all actors.

    The metaclass allows declare the entry point of an actor with the
    decorator ``initial_behavior``.

    """
    def __new__(mcls, name, bases, dict):
        for meth in list(dict.values()):
            if getattr(meth, 'initial_behavior', False):
                dict['behavior'] = meth
        return type.__new__(mcls, name, bases, dict)
        
        
class AbstractActor(object, metaclass=MetaActor):
    """Base class for all actors."""

    def __init__(self, **kwargs):
        """Initialize by setting all keyword arguments.

        This constructor *does not* create the actor. It just binds
        the keyword arguments so behaviors can be re-used by other
        actors.

        To *create* an actor use the classmethod ``create``.

        """
        self.setup()
        self.__dict__.update(kwargs)

    def setup(self):
        """Easy hook for initializing state.

        To avoid having to overload the __init__ method and having to
        call super, this method can be used to set instance variables
        in the actor.

        """
        pass
        
    def __call__(self, message):
        """Send messages.

        Implement in subclasses according to the event loop in use.

        """
        raise NotImplementedError()

    def __lshift__(self, other):
        """Alternative syntax for sending messages.

        Use::

            actor << message

        """
        self(other)
        
    def _ensure_loop(self):
        """Start or make sure the event loop is running."""
        pass

    def error(self, message):
        """Report an error condition.

        Delegate to the sponsor, if it exists, otherwise handle it
        directly.

        """
        if getattr(self, 'sponsor', None) is not None:
            self.sponsor.error(self, message)
        else:
            self._error(message)

    def _error(self, message):
        """Basic error handling for sponsorless actors."""
        print('ERROR: {0}'.format(pprint.pformat(message)))
            
    @classmethod
    def create(cls, **kwargs):
        """Create the actor declared by this class.

        Use as::

            foo = Foo(arg1=val1, arg2=val2)

        If the keyword ``sponsor`` is given, use it to delegate the
        creation of the actor.  The attribute ``sponsor`` is also set
        the actor, in such case.

        """
        sponsor = kwargs.get('sponsor', None)
        if sponsor is not None:
            return sponsor.create(cls, **kwargs)
        else:
            actor = cls(**kwargs)
            actor._ensure_loop()
            return actor


class ActorOwnLoop(AbstractActor):
    """An actor that runs its own event loop.

    This actor starts a thread that executes the behavior of the actor
    in response to the messages received through a queue.
    
    """
    def __call__(self, message):
        self.queue.put(message)
        
    def _ensure_loop(self):
        self.queue = queue.Queue()
        self.dispatcher = threading.Thread(
            target=eventloop.individual_loop,
            args=(self.queue, self),
            name=self._thread_name())
        self.dispatcher.start()

    def _thread_name(self):
        return '{}-{}'.format(
            self.__class__.__name__,
            hex(id(self)))
        
        
class ActorGlobalLoop(AbstractActor):
    """An actor that uses a global event loop.

    Use the ``ThreadedEventLoop`` from the ``eventloop`` module, and
    send messages by scheduling the events.

    """
    def __call__(self, message):
        self.loop.schedule(message, self)

    def _ensure_loop(self):
        self.loop = eventloop.ThreadedEventLoop.get_loop()


class ActorManualLoop(AbstractActor):
    """An actor that has to be run manually.

    This actor is used in cases where a batch of messages have to be
    processed and then finish, for example, when testing an actor.

    The method ``run`` processes all the messages since the creation
    of the actor, or since the last invocation of ``run``.
    
    """
    
    def __call__(self, message):
        self.loop.schedule(message, self)
    
    def _ensure_loop(self):
        self.loop = eventloop.ManualEventLoop.get_loop()

    def run(self):
        self.loop.run()
        

class ActorOwnManualLoop(AbstractActor):
    """Full manual actor.

    This actor processes messages by invoking its method ``act``.
    ``act`` processes one message, if available, and blocks waiting
    for one if there is none.

    The method ``act`` returns whatever the behavior returns.
    
    """

    def __call__(self, message):
        self.queue.put(message)

    def _ensure_loop(self):
        self.queue = queue.Queue()
        
    def run(self):
        eventloop.individual_loop(self.queue, self)

    def act(self):
        return eventloop.individual_loop_step(self.queue, self)
        

class Wait(ActorOwnManualLoop):
    """Use a full manual actor for synchronization purposes.

    This actor can be used to receive messages in the current
    execution context.  It is useful for obtaining final results from
    actors before finishing, for example.

    Use as::

        w = Wait()
        result = w.act()   # wait for a message from some actor
                           # and return the message

    """
    @initial_behavior
    def wait_beh(self, message):
        return message


#Actor = ActorOwnLoop
#Actor = ActorManualLoop

Actor = ActorGlobalLoop

