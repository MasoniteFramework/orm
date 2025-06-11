class scope:
    def __init__(self, callback, *params, **kwargs):
        self.fn = callback

    def __set_name__(self, cls, name):
        if cls not in cls._scopes:
            cls._scopes[cls] = {name: self.fn}
        else:
            cls._scopes[cls].update({name: self.fn})
        self.cls = cls

    def __call__(self, *args, **kwargs):
        instantiated = self.cls()
        builder = instantiated.get_builder()
        return self.fn(instantiated, builder, *args, **kwargs)
