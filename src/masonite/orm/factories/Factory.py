from faker import Faker


class Factory:

    _factories = {}

    def __init__(self, model, number=1):
        self.model = model
        self.number = number

    def make(self, dictionary={}, name="default"):
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

    def create(self, dictionary={}, name="default"):
        if self.number == 1 and not isinstance(dictionary, list):
            called = self._factories[self.model][name](Faker())
            called.update(dictionary)
            return self.model.create(called)

        elif isinstance(dictionary, list):
            results = []
            for index in range(0, len(dictionary)):
                called = self._factories[self.model][name](Faker())
                called.update(dictionary)
                results.append(called)
            return self.model.create(results)
        else:
            full_collection = []
            for index in range(0, self.number):
                called = self._factories[self.model][name](Faker())
                called.update(dictionary)
                full_collection.append(called)
                self.model.create(called)

            return self.model.hydrate(full_collection)

    @classmethod
    def register(cls, model, call, name="default"):
        if model not in cls._factories:
            cls._factories[model] = {name: call}
        else:
            cls._factories[model][name] = call
