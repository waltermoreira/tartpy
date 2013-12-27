class AbstractSponsor(object):

    def create(self, cls, **kwargs):
        raise NotImplementedError()


class SimpleSponsor(AbstractSponsor):

    def create(self, cls, **kwargs):
        actor = cls(**kwargs)
        return actor

