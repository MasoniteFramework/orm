import inspect
import unittest

from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar


class BaseInsertGrammarTest:
    def setUp(self):
        self.builder = QueryBuilder(SQLiteGrammar, table="users")

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

    def test_can_compile_bulk_create(self):
        to_sql = self.builder.bulk_create(
            [{"name": "Joe"}, {"name": "Bill"}, {"name": "John"}], query=True
        ).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_bulk_create_qmark(self):
        to_sql = self.builder.bulk_create(
            [{"name": "Joe"}, {"name": "Bill"}, {"name": "John"}], query=True
        ).to_qmark()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_bulk_create_multiple(self):
        to_sql = self.builder.bulk_create(
            [
                {"name": "Joe", "active": "1"},
                {"name": "Bill", "active": "1"},
                {"name": "John", "active": "1"},
            ],
            query=True,
        ).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)


class TestSqliteUpdateGrammar(BaseInsertGrammarTest, unittest.TestCase):

    grammar = "sqlite"

    def can_compile_insert(self):
        """
        self.builder.create({
            'name': 'Joe'
        }).to_sql()
        """
        return """INSERT INTO "users" ("name") VALUES ('Joe')"""

    def can_compile_insert_with_keywords(self):
        """
        self.builder.create(name="Joe").to_sql()
        """
        return """INSERT INTO "users" ("name") VALUES ('Joe')"""

    def can_compile_bulk_create(self):
        """
        self.builder.create(name="Joe").to_sql()
        """
        return """INSERT INTO "users" ("name") VALUES ('Joe'), ('Bill'), ('John')"""

    def can_compile_bulk_create_multiple(self):
        """
        self.builder.create(name="Joe").to_sql()
        """
        return """INSERT INTO "users" ("name", "active") VALUES ('Joe', '1'), ('Bill', '1'), ('John', '1')"""

    def can_compile_bulk_create_qmark(self):
        """
        self.builder.create(name="Joe").to_sql()
        """
        return """INSERT INTO "users" ("name") VALUES ('?'), ('?'), ('?')"""
