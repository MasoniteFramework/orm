import os
import unittest

from src.masoniteorm import Factory as factory
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder


class User(Model):
    pass


class AfterCreatedModel(Model):
    __dry__ = True
    pass


class TestFactories(unittest.TestCase):
    def setUp(self):
        factory.register(User, self.user_factory)
        factory.register(User, self.named_user_factory, name="admin")
        factory.register(AfterCreatedModel, self.named_user_factory)
        factory.after_creating(AfterCreatedModel, self.after_creating)

    def user_factory(self, faker):
        return {"id": 1, "name": faker.name()}

    def named_user_factory(self, faker):
        return {"id": 1, "name": faker.name(), "admin": 1}

    def after_creating(self, model, faker):
        model.after_created = True

    def test_can_make_single(self):
        user = factory(User).make({"id": 1, "name": "Joe"})

        self.assertEqual(user.name, "Joe")
        self.assertIsInstance(user, User)

    def test_can_make_several(self):
        users = factory(User).make([{"id": 1, "name": "Joe"}, {"id": 2, "name": "Bob"}])

        self.assertEqual(users.count(), 2)

    def test_can_make_any_number(self):
        users = factory(User, 50).make()

        self.assertEqual(users.count(), 50)

    def test_can_make_named_factory(self):
        user = factory(User).make(name="admin")
        self.assertEqual(user.admin, 1)

    def test_after_creates(self):
        user = factory(AfterCreatedModel).create()
        self.assertTrue(user.name)
        self.assertEqual(user.after_created, True)

        users = factory(AfterCreatedModel).create({"name": "billy"})
        self.assertEqual(users.name, "billy")
        self.assertEqual(users.after_created, True)

        users = factory(AfterCreatedModel).make()
        self.assertEqual(users.after_created, True)

        users = factory(AfterCreatedModel, 2).make()
        for user in users:
            self.assertEqual(user.after_created, True)
