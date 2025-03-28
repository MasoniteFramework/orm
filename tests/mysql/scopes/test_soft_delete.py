import unittest

import pendulum

from tests.integrations.config.database import DATABASES
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import MySQLGrammar
from src.masoniteorm.scopes import SoftDeleteScope
from tests.utils import MockConnectionFactory

from src.masoniteorm.models import Model
from src.masoniteorm.scopes import SoftDeletesMixin


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
        sql = "SELECT * FROM `users`"
        builder = self.get_builder().set_global_scope(SoftDeleteScope())
        self.assertEqual(sql, builder.with_trashed().to_sql())

    def test_force_delete(self):
        sql = "DELETE FROM `users`"
        builder = self.get_builder().set_global_scope(SoftDeleteScope())
        self.assertEqual(sql, builder.force_delete(query=True).to_sql())

    def test_restore(self):
        sql = "UPDATE `users` SET `users`.`deleted_at` = 'None'"
        builder = self.get_builder().set_global_scope(SoftDeleteScope())
        self.assertEqual(sql, builder.restore().to_sql())

    def test_force_delete_with_wheres(self):
        sql = "DELETE FROM `users` WHERE `users`.`active` = '1'"
        builder = self.get_builder().set_global_scope(SoftDeleteScope())
        self.assertEqual(
            sql, UserSoft.where("active", 1).force_delete(query=True).to_sql()
        )

    def test_that_trashed_users_are_not_returned_by_default(self):
        sql = "SELECT * FROM `users` WHERE `users`.`deleted_at` IS NULL"
        builder = self.get_builder().set_global_scope(SoftDeleteScope())
        self.assertEqual(sql, builder.to_sql())

    def test_only_trashed(self):
        sql = "SELECT * FROM `users` WHERE `users`.`deleted_at` IS NOT NULL"
        builder = self.get_builder().set_global_scope(SoftDeleteScope())
        self.assertEqual(sql, builder.only_trashed().to_sql())

    def test_only_trashed_on_model(self):
        sql = "SELECT * FROM `users` WHERE `users`.`deleted_at` IS NOT NULL"
        self.assertEqual(sql, UserSoft.only_trashed().to_sql())

    def test_can_change_column(self):
        sql = "SELECT * FROM `users` WHERE `users`.`archived_at` IS NOT NULL"
        self.assertEqual(sql, UserSoftArchived.only_trashed().to_sql())

    def test_find_with_global_scope(self):
        find_sql = UserSoft.find("1", query=True).to_sql()
        raw_sql = """SELECT * FROM `users` WHERE `users`.`id` = '1' AND `users`.`deleted_at` IS NULL"""
        self.assertEqual(find_sql, raw_sql)

    def test_find_with_trashed_scope(self):
        find_sql = UserSoft.with_trashed().find("1", query=True).to_sql()
        raw_sql = """SELECT * FROM `users` WHERE `users`.`id` = '1'"""
        self.assertEqual(find_sql, raw_sql)

    def test_find_with_only_trashed_scope(self):
        find_sql = UserSoft.only_trashed().find("1", query=True).to_sql()
        raw_sql = """SELECT * FROM `users` WHERE `users`.`deleted_at` IS NOT NULL AND `users`.`id` = '1'"""
        self.assertEqual(find_sql, raw_sql)
