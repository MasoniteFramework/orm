from types import SimpleNamespace


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
        cls.__has_events__ = True
        return cls

    @classmethod
    def creating(cls, callback):
        cls._register_model_event('creating', callback)

    @classmethod
    def created(cls, callback):
        cls._register_model_event('created', callback)

    @classmethod
    def deleting(cls, callback):
        cls._register_model_event('deleting', callback)

    @classmethod
    def deleted(cls, callback):
        cls._register_model_event('deleted', callback)

    @classmethod
    def hydrating(cls, callback):
        cls._register_model_event('hydrating', callback)

    @classmethod
    def hydrated(cls, callback):
        cls._register_model_event('hydrated', callback)

    @classmethod
    def saving(cls, callback):
        cls._register_model_event('saving', callback)

    @classmethod
    def saved(cls, callback):
        cls._register_model_event('saved', callback)

    @classmethod
    def updating(cls, callback):
        cls._register_model_event('updating', callback)

    @classmethod
    def updated(cls, callback):
        cls._register_model_event('updated', callback)

    @classmethod
    def _register_model_event(cls, event, callback):
        anon_observer = SimpleNamespace()
        anon_observer.__setattr__(event, callback)
        cls.observe(anon_observer)