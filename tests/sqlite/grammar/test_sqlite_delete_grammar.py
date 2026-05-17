import unittest

from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar


class TestSQLiteDeleteGrammar(unittest.TestCase):
    def setUp(self):
        self.builder = QueryBuilder(SQLiteGrammar, table="users")

    def test_can_compile_delete(self):
        query_sql = self.builder.delete("id", 1, query=True).to_sql()
        expected_sql = """DELETE FROM "users" WHERE "id" = '1'"""
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_delete_in(self):
        query_sql = self.builder.delete("id", [1, 2, 3], query=True).to_sql()
        expected_sql = """DELETE FROM "users" WHERE "id" IN ('1','2','3')"""
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_delete_with_where(self):
        query_sql = (
            self.builder.where("age", 20)
            .where("profile", 1)
            .set_action("delete")
            .delete(query=True)
            .to_sql()
        )
        expected_sql = (
            """DELETE FROM "users" WHERE "age" = '20' AND "profile" = '1'"""
        )
        self.assertEqual(query_sql, expected_sql)
