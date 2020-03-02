import os
import unittest

from src.masonite.orm.models.Model import Model
from src.masonite.orm.relationships import belongs_to, has_many

if os.getenv("RUN_MYSQL_DATABASE", False) == "True":

    class Profile(Model):
        __table__ = "profiles"

    class Articles(Model):
        __table__ = "articles"

    class MockUser(Model):

        _eager_loads = ()

        __table__ = "users"

        @belongs_to("id", "user_id")
        def profile(self):
            return Profile

        @has_many("id", "user_id")
        def articles(self):
            return Articles

    class TestRelationships(unittest.TestCase):
        def test_relationship_can_be_callable(self):
            self.assertEqual(
                MockUser.profile().where("name", "Joe").to_sql(),
                "SELECT * FROM `profiles` WHERE `name` = 'Joe'",
            )

        def test_can_access_relationship(self):
            for dictionary in MockUser.where("id", 1).get():
                user = MockUser.hydrate(dictionary)
                self.assertIsInstance(user.profile, Profile)
                print(user.profile.city)

        def test_can_access_has_many_relationship(self):
            user = MockUser.hydrate(MockUser.where("id", 1).first())
            self.assertEqual(len(user.articles), 4)

        def test_can_access_relationship_multiple_times(self):
            user = MockUser.hydrate(MockUser.where("id", 1).first())
            self.assertEqual(len(user.articles), 4)
            self.assertEqual(len(user.articles), 4)

        def test_loading(self):
            users = MockUser.with_("articles").get()
            for user in users:
                user_model = MockUser.hydrate(user)
                print(user_model.id)
                print(user_model.articles)
