class scope:
    def __init__(self, callback, *params, **kwargs):
        self.fn = callback

    def __set_name__(self, cls, name):
        self.cls = cls
        self.scope_name = name

    def __call__(self, *args, **kwargs):
        instantiated = self.cls()
        builder = instantiated.get_builder()
        builder._scopes.update({self.scope_name: self.fn})
        return self.fn(instantiated, builder, *args, **kwargs)
