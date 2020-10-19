import inspect
import unittest

from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar


class BaseDeleteGrammarTest:
    def setUp(self):
        self.builder = QueryBuilder(SQLiteGrammar, table="users")

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
            .delete(query=True)
            .to_sql()
        )

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)


class TestSqliteDeleteGrammar(BaseDeleteGrammarTest, unittest.TestCase):

    grammar = "sqlite"

    def can_compile_delete(self):
        """
        (
            self.builder
            .delete('id', 1)
            .to_sql()
        )
        """
        return """DELETE FROM "users" WHERE "id" = '1'"""

    def can_compile_delete_in(self):
        """
        (
            self.builder
            .delete('id', 1)
            .to_sql()
        )
        """
        return """DELETE FROM "users" WHERE "id" IN ('1','2','3')"""

    def can_compile_delete_with_where(self):
        """
        (
            self.builder
            .where('age', 20)
            .where('profile', 1)
            .delete()
            .to_sql()
        )
        """
        return """DELETE FROM "users" WHERE "age" = '20' AND "profile" = '1'"""
