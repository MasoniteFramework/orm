import unittest
from src.masoniteorm.models import Model

class User(Model):
    __connection__ = "t"

    @property
    def profile(self):
        return self.has_one(Profile, "user_id", "id")
    
class Profile(Model):
    __connection__ = "t"

    @property
    def user(self):
        return self.has_one(User, "id", "user_id")



class TestRelatinships(unittest.TestCase):

    def test_can_get_owner_value(self):
        user = User.find(1)
        self.assertEqual(user.name, "bill")

    def test_can_get_has_one_related_value(self):
        user = User.find(1)
        self.assertEqual(user.name, "bill")
        self.assertEqual(user.profile.title, "title")

    def test_can_get_has_one_query_builder(self):
        user = User.find(1)
        self.assertEqual(user.name, "bill")
        self.assertEqual(user.profile().to_sql(), 'SELECT * FROM "profiles" WHERE "profiles"."user_id" = \'1\'')

    def test_can_get_eager_load_from_builder(self):
        user = User.with_("profile").find(1)
        self.assertEqual(user.name, "bill")
        self.assertEqual(user.profile.title, 'title')

    def test_can_get_nested_eager_load_from_builder(self):
        user = User.with_("profile.user").find(1)
        self.assertEqual(user.profile.user.name, "bill")
        self.assertEqual(user.profile.user.name, "bill")
        self.assertEqual(user.profile.user.name, "bill")
        self.assertEqual(user.profile.user.name, "bill")
        self.assertEqual(user.profile.user.name, "bill")
        self.assertEqual(user.profile.user.name, "bill")
        self.assertEqual(user.profile.user.name, "bill")
        self.assertEqual(user.profile.user.name, "bill")
        self.assertEqual(user.profile.user.name, "bill")
        self.assertEqual(user.profile.user.name, "bill")
        self.assertEqual(user.profile.user.name, "bill")
        self.assertEqual(user.profile.user.name, "bill")
        self.assertEqual(user.profile.user.name, "bill")
        self.assertEqual(user.profile.user.name, "bill")
        self.assertEqual(user.profile.user.name, "bill")