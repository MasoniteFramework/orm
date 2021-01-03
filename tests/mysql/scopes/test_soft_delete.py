import inspect
import unittest

from config.database import DATABASES
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
        )

    def test_with_trashed(self):
        sql = "SELECT * FROM `users`"
        builder = self.get_builder().set_global_scope(SoftDeleteScope())
        self.assertEqual(sql, builder.with_trashed().to_sql())

    def test_that_trashed_users_are_not_returned_by_default(self):
        sql = "SELECT * FROM `users` WHERE `users`.`deleted_at` IS NULL"
        builder = self.get_builder().set_global_scope(SoftDeleteScope())
        self.assertEqual(sql, builder.to_sql())

    def test_only_trashed(self):
        sql = "SELECT * FROM `users` WHERE `users`.`deleted_at` IS NOT NULL"
        builder = self.get_builder().set_global_scope(SoftDeleteScope())
        self.assertEqual(sql, builder.only_trashed().to_sql())
