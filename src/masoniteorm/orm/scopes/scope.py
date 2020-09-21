import inspect


class scope:
    def __init__(self, callback, *params, **kwargs):
        self.fn = callback

    def __set_name__(self, cls, name):
        cls._scopes.update({name: self.fn})
        self.cls = cls

    def __call__(self, *args, **kwargs):
        instantiated = self.cls()
        builder = instantiated.get_builder()
        return self.fn(instantiated, builder, *args, **kwargs)
