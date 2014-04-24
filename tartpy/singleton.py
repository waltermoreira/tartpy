"""

Singleton
=========

Metaclass to make a class a singleton.

Use as::

    class MySingleton(object, metaclass=Singleton): ...

"""

class Singleton(type):
    
    def __init__(self, name, bases, namespace):
        super().__init__(name, bases, namespace)
        self.instances = {}

    def __call__(self, *args, **kwargs):
        return self.instances.setdefault(
            args, super().__call__(*args, **kwargs))
            
