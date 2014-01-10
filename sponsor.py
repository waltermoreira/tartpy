"""

Sponsor objects
===============

Sponsors are objects that can manage resources for actor allocations.
Creation and error reporting can be delegated to them when an actor is
create with a keyword argument of the form::

    Actor.create(sponsor=obj)

"""

import queue


class AbstractSponsor(object):
    """Interface for sponsors."""

    def create(self, cls, **kwargs):
        """Create an actor from ``cls``."""
        raise NotImplementedError()

    def error(self, actor, message):
        """Report error from ``actor``."""
        raise NotImplementedError()
        

class SimpleSponsor(AbstractSponsor):
    """Sponsor that keeps track of created actors."""
    
    def __init__(self):
        self.actors = queue.LifoQueue()
        
    def create(self, cls, **kwargs):
        self.actors.put((cls, kwargs))
        actor = cls(**kwargs)
        actor._ensure_loop()
        return actor

    def error(self, actor, message):
        print('ERROR (Actor {0}): {1}'.format(actor, message))