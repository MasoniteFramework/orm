import inspect


class scope:
    def __init__(self, callback, *params, **kwargs):
        self.fn = callback

    def __set_name__(self, cls, name):
        cls.boot()
        cls.builder.set_scope(cls, name)
        self.cls = cls

    def __call__(self, *args, **kwargs):
        # self.cls.boot()
        self.fn(self.cls.builder, *args, **kwargs)
        return self.cls.builder
