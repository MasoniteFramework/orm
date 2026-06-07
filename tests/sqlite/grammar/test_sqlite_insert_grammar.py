import unittest

from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar


class TestSQLiteInsertGrammar(unittest.TestCase):
    def setUp(self):
        self.builder = QueryBuilder(SQLiteGrammar, table="users")

    def test_can_compile_insert(self):
        query_sql = self.builder.create({"name": "Joe"}, query=True).to_sql()
        expected_sql = """INSERT INTO "users" ("name") VALUES ('Joe')"""
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_insert_with_keywords(self):
        query_sql = self.builder.create(name="Joe", query=True).to_sql()
        expected_sql = """INSERT INTO "users" ("name") VALUES ('Joe')"""
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_bulk_create(self):
        # Keys are intentionally out of order to verify column-to-value alignment
        query_sql = self.builder.bulk_create(
            [
                {"name": "Joe", "age": 5},
                {"age": 35, "name": "Bill"},
                {"name": "John", "age": 10},
            ],
            query=True,
        ).to_sql()
        expected_sql = """INSERT INTO "users" ("age", "name") VALUES ('5', 'Joe'), ('35', 'Bill'), ('10', 'John')"""
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_bulk_create_multiple(self):
        query_sql = self.builder.bulk_create(
            [
                {"name": "Joe", "active": "1"},
                {"name": "Bill", "active": "1"},
                {"name": "John", "active": "1"},
            ],
            query=True,
        ).to_sql()
        expected_sql = """INSERT INTO "users" ("active", "name") VALUES ('1', 'Joe'), ('1', 'Bill'), ('1', 'John')"""
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_bulk_create_qmark(self):
        query_sql = self.builder.bulk_create(
            [{"name": "Joe"}, {"name": "Bill"}, {"name": "John"}], query=True
        ).to_qmark()
        expected_sql = """INSERT INTO "users" ("name") VALUES (?), (?), (?)"""
        self.assertEqual(query_sql, expected_sql)
