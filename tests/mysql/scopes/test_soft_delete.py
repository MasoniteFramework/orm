import inspect
import unittest

from tests.integrations.config.database import DATABASES
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import MySQLGrammar
from src.masoniteorm.scopes import SoftDeleteScope
from tests.utils import MockConnectionFactory

from src.masoniteorm.models import Model
from src.masoniteorm.scopes import SoftDeletesMixin
from tests.User import User


class UserSoft(Model, SoftDeletesMixin):
    __dry__ = True


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
        self.assertEqual(sql, builder.force_delete().to_sql())

    def test_restore(self):
        sql = "UPDATE `users` SET `users`.`deleted_at` = 'None'"
        builder = self.get_builder().set_global_scope(SoftDeleteScope())
        self.assertEqual(sql, builder.restore().to_sql())

    def test_force_delete_with_wheres(self):
        sql = "DELETE FROM `user_softs` WHERE `user_softs`.`active` = '1'"
        builder = self.get_builder().set_global_scope(SoftDeleteScope())
        self.assertEqual(sql, UserSoft.where("active", 1).force_delete().to_sql())

    def test_that_trashed_users_are_not_returned_by_default(self):
        sql = "SELECT * FROM `users` WHERE `users`.`deleted_at` IS NULL"
        builder = self.get_builder().set_global_scope(SoftDeleteScope())
        self.assertEqual(sql, builder.to_sql())

    def test_only_trashed(self):
        sql = "SELECT * FROM `users` WHERE `users`.`deleted_at` IS NOT NULL"
        builder = self.get_builder().set_global_scope(SoftDeleteScope())
        self.assertEqual(sql, builder.only_trashed().to_sql())

    def test_only_trashed_on_model(self):
        sql = "SELECT * FROM `user_softs` WHERE `user_softs`.`deleted_at` IS NOT NULL"
        self.assertEqual(sql, UserSoft.only_trashed().to_sql())
