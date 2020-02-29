class BelongsTo:
    def __init__(self, callback, *params, **kwargs):
        self.fn = callback

    def __set_name__(self, cls, name):
        cls.boot()
        self.cls = cls

    def __call__(self, fn=None, *args, **kwargs):
        if callable(fn):
            self.fn = fn
            return self

        self.relationship = self.fn(self)
        self.relationship.boot()
        return self.relationship.builder

    def __get__(self, instance, owner):
        relationship = self.fn(self)
        if not instance:
            """This means the user called the attribute rather than accessed it.
            In this case we want to return the builder
            """
            self.relationship = self.fn(self)
            self.relationship.boot()
            return self.relationship.builder

        return relationship.hydrate(
            relationship.where("user_id", self.cls.__attributes__["id"]).first()
        )
