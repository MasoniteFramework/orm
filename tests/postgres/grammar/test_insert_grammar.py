import inspect
import unittest

from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import GrammarFactory, PostgresGrammar


class BaseInsertGrammarTest:
    grammar = "postgres"

    def setUp(self):
        self.builder = QueryBuilder(GrammarFactory.make("postgres"), table="users")

    def test_can_compile_insert(self):
        to_sql = self.builder.create({"name": "Joe"}, query=True).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_insert_with_keywords(self):
        to_sql = self.builder.create(name="Joe", query=True).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)


class TestPostgresUpdateGrammar(BaseInsertGrammarTest, unittest.TestCase):

    grammar = "postgres"

    def can_compile_insert(self):
        """
        self.builder.create({
            'name': 'Joe'
        }).to_sql()
        """
        return """INSERT INTO "users" ("name") VALUES ('Joe') RETURNING *"""

    def can_compile_insert_with_keywords(self):
        """
        self.builder.create(name="Joe").to_sql()
        """
        return """INSERT INTO "users" ("name") VALUES ('Joe') RETURNING *"""
