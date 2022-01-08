class ObservesEvents:
    def observe_events(self, model, event):
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
