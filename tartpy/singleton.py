class Singleton(type):
    
    def __init__(self, name, bases, namespace):
        super().__init__(name, bases, namespace)
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = super().__call__(*args, **kwargs)
        return self.instance
            
