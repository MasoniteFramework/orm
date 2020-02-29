import os
import unittest

from src.masonite.orm.models.Model import Model

if os.getenv('RUN_MYSQL_DATABASE', False) == 'True':
    class belongs_to:

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

            return relationship.hydrate(relationship.where('user_id', self.cls.__attributes__['id']).first())

    class Profile(Model):
        __table__ = 'profiles'

    class MockUser(Model):

        _eager_loads = ()

        __table__ = 'users'

        @belongs_to('id', 'user_id')
        def profile(self):
            return Profile

        @classmethod
        def with_(cls, *eagers):
            cls.boot()
            cls._eager_loads += eagers
            return cls.builder


    class TestRelationships(unittest.TestCase):

        def test_relationship_can_be_callable(self):
            self.assertEqual(
                MockUser.profile().where('name', 'Joe').to_sql(),
                "SELECT * FROM `profiles` WHERE `name` = 'Joe'"
            )

        def test_can_access_relationship(self):
            for dictionary in MockUser.where('id', 1).get():
                user = MockUser.hydrate(dictionary)
                self.assertIsInstance(user.profile, Profile)
                print(user.profile.city)
