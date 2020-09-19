import os
import unittest

from src.masoniteorm.orm import Factory as factory
from src.masoniteorm.orm.builder import QueryBuilder
from src.masoniteorm.orm.query.grammars import GrammarFactory, MySQLGrammar
from src.masoniteorm.orm.models import Model


class User(Model):
    pass


class TestFactories(unittest.TestCase):
    def setUp(self):
        factory.register(User, self.user_factory)
        factory.register(User, self.named_user_factory, name="admin")

    def user_factory(self, faker):
        return {"id": 1, "name": faker.name()}

    def named_user_factory(self, faker):
        return {"id": 1, "name": faker.name(), "admin": 1}

    def test_can_make_single(self):
        user = factory(User).make({"id": 1, "name": "Joe"})

        self.assertEqual(user.name, "Joe")
        self.assertIsInstance(user, User)

    def test_can_make_several(self):
        users = factory(User).make(
            [{"id": 1, "name": "Joe"}, {"id": 2, "name": "Bob"},]
        )

        self.assertEqual(users.count(), 2)

    def test_can_make_any_number(self):
        users = factory(User, 50).make()

        self.assertEqual(users.count(), 50)

    def test_can_make_named_factory(self):
        user = factory(User).make(name="admin")
        self.assertEqual(user.admin, 1)

    # def test_can_create(self):
    #     user = factory(User).create()
    #     self.assertTrue(user.name)
