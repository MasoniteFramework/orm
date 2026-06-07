import unittest

from src.masoniteorm.expressions import Raw
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar


class TestSQLiteUpdateGrammar(unittest.TestCase):
    def setUp(self):
        self.builder = QueryBuilder(SQLiteGrammar, table="users")

    def test_can_compile_update(self):
        query_sql = (
            self.builder.where("name", "bob")
            .update({"name": "Joe"}, dry=True)
            .to_sql()
        )
        expected_sql = (
            """UPDATE "users" SET "name" = 'Joe' WHERE "name" = 'bob'"""
        )
        self.assertEqual(query_sql, expected_sql)

    def test_raw_expression(self):
        query_sql = self.builder.update(
            {"name": Raw('"username"')}, dry=True
        ).to_sql()
        expected_sql = """UPDATE "users" SET "name" = "username\""""
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_multiple_update(self):
        query_sql = self.builder.update(
            {"name": "Joe", "email": "user@email.com"}, dry=True
        ).to_sql()
        expected_sql = (
            """UPDATE "users" SET "name" = 'Joe', "email" = 'user@email.com'"""
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_update_with_multiple_where(self):
        query_sql = (
            self.builder.where("name", "bob")
            .where("age", 20)
            .update({"name": "Joe"}, dry=True)
            .to_sql()
        )
        expected_sql = """UPDATE "users" SET "name" = 'Joe' WHERE "name" = 'bob' AND "age" = '20'"""
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_increment(self):
        query_sql = self.builder.increment("age", dry=True).to_sql()
        expected_sql = """UPDATE "users" SET "age" = "age" + '1'"""
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_decrement(self):
        query_sql = self.builder.decrement("age", 20, dry=True).to_sql()
        expected_sql = """UPDATE "users" SET "age" = "age" - '20'"""
        self.assertEqual(query_sql, expected_sql)
