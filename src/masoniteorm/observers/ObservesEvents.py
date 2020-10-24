class ObservesEvents:
    def observe_events(self, model, event):
        for observer in model.__observers__:
            try:
                getattr(observer, event)(model)
            except AttributeError:
                pass
