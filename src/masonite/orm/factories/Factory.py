from faker import Faker

class Factory:

    _factories = {}

    def __init__(self, model, number=1):
        self.model = model
        self.number = number

    def make(self, dictionary={}, name='default'):
        if self.number == 1 and not isinstance(dictionary, list):
            called = self._factories[self.model][name](Faker())
            called.update(dictionary)
            return self.model.hydrate(called)
        elif isinstance(dictionary, list):
            results = []
            for index in range(0, len(dictionary)):
                called = self._factories[self.model][name](Faker())
                called.update(dictionary)
                results.append(called)
            return self.model.hydrate(results)
        else:
            results = []
            for index in range(0, self.number):
                called = self._factories[self.model][name](Faker())
                called.update(dictionary)
                results.append(called)
            return self.model.hydrate(results)

    @classmethod
    def register(cls, model, call, name='default'):
        print(cls._factories)
        if not model in cls._factories:
            cls._factories[model] = {name: call}
        else:
            cls._factories[model][name] = call