import inspect
import unittest

from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import PostgresGrammar


class BaseDeleteGrammarTest:
    def setUp(self):
        self.builder = QueryBuilder(PostgresGrammar, table="users")

    def test_can_compile_delete(self):
        to_sql = self.builder.delete("id", 1, query=True).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_delete_in(self):
        to_sql = self.builder.delete("id", [1, 2, 3], query=True).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_delete_with_where(self):
        to_sql = (
            self.builder.where("age", 20)
            .where("profile", 1)
            .set_action("delete")
            .delete(query=True)
            .to_sql()
        )

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)


class TestPostgresDeleteGrammar(BaseDeleteGrammarTest, unittest.TestCase):

    grammar = "postgres"

    def can_compile_delete(self):
        """
        (
            self.builder
            .delete('id', 1)
            .to_sql()
        )
        """
        return """DELETE FROM "users" WHERE "users"."id" = '1'"""

    def can_compile_delete_in(self):
        """
        (
            self.builder
            .delete('id', 1)
            .to_sql()
        )
        """
        return """DELETE FROM "users" WHERE "users"."id" IN ('1','2','3')"""

    def can_compile_delete_with_where(self):
        """
        (
            self.builder
            .where('age', 20)
            .where('profile', 1)
            .set_action('delete')
            .delete()
            .to_sql()
        )
        """
        return """DELETE FROM "users" WHERE "users"."age" = '20' AND "users"."profile" = '1'"""
