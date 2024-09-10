import unittest

from src.masoniteorm.models import Model
from src.masoniteorm.scopes import SoftDeletesMixin


class User(Model, SoftDeletesMixin):
    pass


class TestModelScopes(unittest.TestCase):
    def test_find_with_global_scope(self):
        user_where = User.where("id", 1).to_sql()
        user_find = User.find("1", query=True)
        self.assertEqual(user_where, user_find)

    def test_find_with_trashed_scope(self):
        user_where = User.with_trashed().where("id", 1).to_sql()
        user_find = User.with_trashed().find("1", query=True)
        self.assertEqual(user_where, user_find)

    def test_find_with_only_trashed_scope(self):
        user_where = User.only_trashed().where("id", 1).to_sql()
        user_find = User.only_trashed().find("1", query=True)
        self.assertEqual(user_where, user_find)
