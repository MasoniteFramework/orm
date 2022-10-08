class ObservesEvents:
    def observe_events(self, model, event):
        if model.__has_events__ == True:
            for observer in model.__observers__.get(model.__class__, []):
                try:
                    getattr(observer, event)(model)
                except AttributeError:
                    pass

    @classmethod
    def observe(cls, observer):
        if cls in cls.__observers__:
            cls.__observers__[cls].append(observer)
        else:
            cls.__observers__.update({cls: [observer]})

    @classmethod
    def without_events(cls):
        """Sets __has_events__ attribute on model to false."""
        cls.__has_events__ = False
        return cls

    @classmethod
    def with_events(cls):
        """Sets __has_events__ attribute on model to True."""
        cls.__has_events__ = False
        return cls
