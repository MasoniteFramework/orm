import inspect
import unittest

from src.masoniteorm.orm.query import QueryBuilder
from src.masoniteorm.orm.query.grammars import MySQLGrammar
from src.masoniteorm.orm.models import Model
from src.masoniteorm.orm.relationships import has_many
from tests.utils import MockConnectionFactory
from config.database import DATABASES
from src.masoniteorm.orm.scopes import SoftDeleteScope


class BaseTestQueryBuilderScopes(unittest.TestCase):
    grammar = "mysql"

    def get_builder(self, table="users"):
        connection = MockConnectionFactory().make("default")
        return QueryBuilder(
            grammar=MySQLGrammar,
            connection=connection,
            table=table,
            model=None,
            connection_details=DATABASES,
        )

    def test_scopes(self):
        builder = self.get_builder().set_scope(
            "gender", lambda model, q: q.where("gender", "w")
        )

        self.assertEqual(
            builder.gender().where("id", 1).to_sql(),
            "SELECT * FROM `users` WHERE `users`.`gender` = 'w' AND `users`.`id` = '1'",
        )

    def test_global_scopes(self):
        builder = self.get_builder().set_global_scope(
            "where_not_null", lambda q: q.where_not_null("deleted_at"), action="select"
        )

        self.assertEqual(
            builder.where("id", 1).to_sql(),
            "SELECT * FROM `users` WHERE `users`.`id` = '1' AND `users`.`deleted_at` IS NOT NULL",
        )

    def test_global_scope_from_class(self):
        builder = self.get_builder().set_global_scope(SoftDeleteScope())

        self.assertEqual(
            builder.where("id", 1).to_sql(),
            "SELECT * FROM `users` WHERE `users`.`id` = '1' AND `users`.`deleted_at` IS NULL",
        )

    def test_global_scope_remove_from_class(self):
        builder = (
            self.get_builder()
            .set_global_scope(SoftDeleteScope())
            .remove_global_scope(SoftDeleteScope())
        )

        self.assertEqual(
            builder.where("id", 1).to_sql(),
            "SELECT * FROM `users` WHERE `users`.`id` = '1'",
        )

    def test_global_scope_adds_method(self):
        builder = self.get_builder().set_global_scope(SoftDeleteScope())

        self.assertEqual(builder.with_trashed().to_sql(), "SELECT * FROM `users`")
