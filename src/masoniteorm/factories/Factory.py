from faker import Faker
import random


class Factory:

    _factories = {}
    _after_creates = {}
    _faker = None

    @property
    def faker(self):
        if not Factory._faker:
            Factory._faker = Faker()
            random.seed()
            Factory._faker.seed_instance(random.randint(1, 10000))

        return Factory._faker

    def __init__(self, model, number=1):
        self.model = model
        self.number = number

    def make(self, dictionary=None, name="default"):
        if dictionary is None:
            dictionary = {}

        if self.number == 1 and not isinstance(dictionary, list):
            called = self._factories[self.model][name](self.faker)
            called.update(dictionary)
            model = self.model.hydrate(called)
            self.run_after_creates(model)
            return model
        elif isinstance(dictionary, list):
            results = []
            for index in range(0, len(dictionary)):
                called = self._factories[self.model][name](self.faker)
                called.update(dictionary)
                results.append(called)
            models = self.model.hydrate(results)
            for model in models:
                self.run_after_creates(model)
            return models

        else:
            results = []
            for index in range(0, self.number):
                called = self._factories[self.model][name](self.faker)
                called.update(dictionary)
                results.append(called)
            models = self.model.hydrate(results)
            for model in models:
                self.run_after_creates(model)
            return models

    def create(self, dictionary=None, name="default"):
        if dictionary is None:
            dictionary = {}

        if self.number == 1 and not isinstance(dictionary, list):
            called = self._factories[self.model][name](self.faker)
            called.update(dictionary)
            model = self.model.create(called)
            self.run_after_creates(model)
            return model
        elif isinstance(dictionary, list):
            results = []
            for index in range(0, len(dictionary)):
                called = self._factories[self.model][name](self.faker)
                called.update(dictionary)
                results.append(called)

            models = self.model.create(results)
            for model in models:
                self.run_after_creates(model)
            return models
        else:
            full_collection = []
            for index in range(0, self.number):
                called = self._factories[self.model][name](self.faker)
                called.update(dictionary)
                full_collection.append(called)
                model = self.model.create(called)
                self.run_after_creates(model)

            return self.model.hydrate(full_collection)

    @classmethod
    def register(cls, model, call, name="default"):
        if model not in cls._factories:
            cls._factories[model] = {name: call}
        else:
            cls._factories[model][name] = call

    @classmethod
    def after_creating(cls, model, call, name="default"):
        if model not in cls._after_creates:
            cls._after_creates[model] = {name: call}
        else:
            cls._after_creates[model][name] = call

    def run_after_creates(self, model):
        if self.model not in self._after_creates:
            return model

        for name, callback in self._after_creates[self.model].items():
            callback(model, self.faker)
