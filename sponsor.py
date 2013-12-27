class AbstractSponsor(object):

    def create(self, cls, **kwargs):
        raise NotImplementedError()


class SimpleSponsor(AbstractSponsor):

    def __init__(self):
        self.actors = []
        
    def create(self, cls, **kwargs):
        self.actors.append((cls, kwargs))
        actor = cls(**kwargs)
        return actor

