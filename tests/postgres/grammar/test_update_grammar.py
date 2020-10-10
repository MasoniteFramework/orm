from src.masoniteorm.query.grammars import MySQLGrammar
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import GrammarFactory
from src.masoniteorm.connections import PostgresConnection
import unittest
import inspect


class BaseTestCaseUpdateGrammar:
    def setUp(self):
        self.builder = QueryBuilder(
            GrammarFactory.make("postgres"),
            connection=PostgresConnection,
            table="users",
        )

    def test_can_compile_update(self):
        to_sql = (
            self.builder.where("name", "bob").update({"name": "Joe"}, dry=True).to_sql()
        )

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_multiple_update(self):
        to_sql = self.builder.update(
            {"name": "Joe", "email": "user@email.com"}, dry=True
        ).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_update_with_multiple_where(self):
        to_sql = (
            self.builder.where("name", "bob")
            .where("age", 20)
            .update({"name": "Joe"}, dry=True)
            .to_sql()
        )

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_increment(self):
        to_sql = self.builder.increment("age").to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_decrement(self):
        to_sql = self.builder.decrement("age", 20).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)


class TestPostgresUpdateGrammar(BaseTestCaseUpdateGrammar, unittest.TestCase):

    grammar = "postgres"

    def can_compile_update(self):
        """
        builder.where('name', 'bob').update({
            'name': 'Joe'
        }).to_sql()
        """
        return """UPDATE "users" SET "name" = 'Joe' WHERE "name" = 'bob'"""

    def can_compile_multiple_update(self):
        """
        self.builder.update({"name": "Joe", "email": "user@email.com"}, dry=True).to_sql()
        """
        return """UPDATE "users" SET "name" = 'Joe', "email" = 'user@email.com'"""

    def can_compile_update_with_multiple_where(self):
        """
        builder.where('name', 'bob').where('age', 20).update({
            'name': 'Joe'
        }).to_sql()
        """
        return """UPDATE "users" SET "name" = 'Joe' WHERE "name" = 'bob' AND "age" = '20'"""

    def can_compile_increment(self):
        """
        builder.increment('age').to_sql()
        """
        return """UPDATE "users" SET "age" = "age" + '1'"""

    def can_compile_decrement(self):
        """
        builder.decrement('age', 20).to_sql()
        """
        return """UPDATE "users" SET "age" = "age" - '20'"""
