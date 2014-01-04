class AbstractSponsor(object):

    def create(self, cls, **kwargs):
        raise NotImplementedError()

    def error(self, actor, message):
        raise NotImplementedError()
        

class SimpleSponsor(AbstractSponsor):

    def __init__(self):
        self.actors = []
        
    def create(self, cls, **kwargs):
        self.actors.append((cls, kwargs))
        actor = cls(**kwargs)
        return actor

    def error(self, actor, message):
        print('ERROR (Actor {0}): {1}'.format(actor, message))