import inspect
import unittest

from src.masoniteorm.orm.query import QueryBuilder
from src.masoniteorm.orm.query.grammars import SQLiteGrammar
from src.masoniteorm.orm.connections import ConnectionFactory
from src.masoniteorm.orm.models import Model
from src.masoniteorm.orm.relationships import belongs_to
from tests.utils import MockConnectionFactory


class Article(Model):
    __connection__ = "sqlite"
    pass


class User(Model):
    __connection__ = "sqlite"

    @belongs_to("id", "user_id")
    def articles(self):
        return Article


class BaseTestQueryRelationships(unittest.TestCase):
    def get_builder(self, table="users"):
        connection = MockConnectionFactory().make("sqlite")
        return QueryBuilder(
            grammar=SQLiteGrammar, connection=connection, table=table, model=User
        )

    def test_has(self):
        builder = self.get_builder()
        sql = builder.has("articles").to_sql()
        self.assertEqual(
            sql,
            """SELECT * FROM "users" WHERE EXISTS ("""
            """SELECT * FROM "articles" WHERE "articles"."user_id" = "users"."id\""""
            """)""",
        )
