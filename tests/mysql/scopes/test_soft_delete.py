import unittest

from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import MySQLGrammar
from src.masoniteorm.scopes import SoftDeleteScope, SoftDeletesMixin
from tests.integrations.config.database import DATABASES
from tests.utils import MockConnectionFactory


class UserSoft(Model, SoftDeletesMixin):
    __dry__ = True
    __table__ = "users"


class UserSoftArchived(Model, SoftDeletesMixin):
    __dry__ = True
    __deleted_at__ = "archived_at"
    __table__ = "users"


class TestSoftDeleteScope(unittest.TestCase):
    def get_builder(self, table="users"):
        connection = MockConnectionFactory().make("default")
        return QueryBuilder(
            grammar=MySQLGrammar,
            connection_class=connection,
            connection="mysql",
            table=table,
            connection_details=DATABASES,
            dry=True,
        )

    def test_with_trashed(self):
        expected_sql = "SELECT * FROM `users`"
        builder = self.get_builder().set_global_scope(SoftDeleteScope())
        query_sql = builder.with_trashed().to_sql()
        self.assertEqual(query_sql, expected_sql)

    def test_force_delete(self):
        expected_sql = "DELETE FROM `users`"
        builder = self.get_builder().set_global_scope(SoftDeleteScope())
        query_sql = builder.force_delete(query=True).to_sql()
        self.assertEqual(query_sql, expected_sql)

    def test_restore(self):
        expected_sql = "UPDATE `users` SET `users`.`deleted_at` = 'None'"
        builder = self.get_builder().set_global_scope(SoftDeleteScope())
        query_sql = builder.restore().to_sql()
        self.assertEqual(query_sql, expected_sql)

    def test_force_delete_with_wheres(self):
        expected_sql = "DELETE FROM `users` WHERE `users`.`active` = '1'"
        query_sql = (
            UserSoft.where("active", 1).force_delete(query=True).to_sql()
        )
        self.assertEqual(query_sql, expected_sql)

    def test_that_trashed_users_are_not_returned_by_default(self):
        expected_sql = (
            "SELECT * FROM `users` WHERE `users`.`deleted_at` IS NULL"
        )
        builder = self.get_builder().set_global_scope(SoftDeleteScope())
        query_sql = builder.to_sql()
        self.assertEqual(query_sql, expected_sql)

    def test_only_trashed(self):
        expected_sql = (
            "SELECT * FROM `users` WHERE `users`.`deleted_at` IS NOT NULL"
        )
        builder = self.get_builder().set_global_scope(SoftDeleteScope())
        query_sql = builder.only_trashed().to_sql()
        self.assertEqual(query_sql, expected_sql)

    def test_only_trashed_on_model(self):
        expected_sql = (
            "SELECT * FROM `users` WHERE `users`.`deleted_at` IS NOT NULL"
        )
        query_sql = UserSoft.only_trashed().to_sql()
        self.assertEqual(query_sql, expected_sql)

    def test_can_change_column(self):
        expected_sql = (
            "SELECT * FROM `users` WHERE `users`.`archived_at` IS NOT NULL"
        )
        query_sql = UserSoftArchived.only_trashed().to_sql()
        self.assertEqual(query_sql, expected_sql)

    def test_find_with_global_scope(self):
        query_sql = UserSoft.find("1", query=True).to_sql()
        expected_sql = """SELECT * FROM `users` WHERE `users`.`id` = '1' AND `users`.`deleted_at` IS NULL"""
        self.assertEqual(query_sql, expected_sql)

    def test_find_with_trashed_scope(self):
        query_sql = UserSoft.with_trashed().find("1", query=True).to_sql()
        expected_sql = """SELECT * FROM `users` WHERE `users`.`id` = '1'"""
        self.assertEqual(query_sql, expected_sql)

    def test_find_with_only_trashed_scope(self):
        query_sql = UserSoft.only_trashed().find("1", query=True).to_sql()
        expected_sql = """SELECT * FROM `users` WHERE `users`.`deleted_at` IS NOT NULL AND `users`.`id` = '1'"""
        self.assertEqual(query_sql, expected_sql)
