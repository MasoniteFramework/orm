import inspect


class global_scope:
    def __init__(self, callback, *params, **kwargs):
        print("calling global scope")
        self.fn = callback

    def __set_name__(self, cls, name):
        cls.builder.set_global_scope(name, self.fn)
        return self


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
