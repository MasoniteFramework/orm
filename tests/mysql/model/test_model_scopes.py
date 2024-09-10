import unittest

from src.masoniteorm.models import Model
from src.masoniteorm.scopes import SoftDeletesMixin


class User(Model, SoftDeletesMixin):
    pass


class TestModelScopes(unittest.TestCase):
    def test_find_with_global_scope(self):
        find_sql = User.find("1", query=True).to_sql()
        raw_sql = """SELECT * FROM `users` WHERE `users`.`id` = '1' AND `users`.`deleted_at` IS NULL"""
        self.assertEqual(find_sql, raw_sql)

    def test_find_with_trashed_scope(self):
        find_sql = User.with_trashed().find("1", query=True).to_sql()
        raw_sql = """SELECT * FROM `users` WHERE `users`.`id` = '1'"""
        self.assertEqual(find_sql, raw_sql)

    def test_find_with_only_trashed_scope(self):
        find_sql = User.only_trashed().find("1", query=True).to_sql()
        raw_sql = """SELECT * FROM `users` WHERE `users`.`deleted_at` IS NOT NULL AND `users`.`id` = '1'"""
        self.assertEqual(find_sql, raw_sql)
