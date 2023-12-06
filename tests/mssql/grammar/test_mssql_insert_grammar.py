import unittest

from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import MSSQLGrammar


class TestMySQLInsertGrammar(unittest.TestCase):
    def setUp(self):
        self.builder = QueryBuilder(MSSQLGrammar, table="users")

    def test_can_compile_insert(self):
        to_sql = self.builder.create({"name": "Joe"}, query=True).to_sql()

        sql = "INSERT INTO [users] ([users].[name]) VALUES ('Joe')"
        self.assertEqual(to_sql, sql)

    def test_can_compile_bulk_create(self):
        to_sql = self.builder.bulk_create(
            # These keys are intentionally out of order to show column to value alignment works
            [
                {"name": "Joe", "age": 5},
                {"age": 35, "name": "Bill"},
                {"name": "John", "age": 10},
            ],
            query=True,
        ).to_sql()

        sql = "INSERT INTO [users] ([age], [name]) VALUES ('5', 'Joe'), ('35', 'Bill'), ('10', 'John')"
        self.assertEqual(to_sql, sql)

    def test_can_compile_bulk_create_qmark(self):
        to_sql = self.builder.bulk_create(
            [{"name": "Joe"}, {"name": "Bill"}, {"name": "John"}], query=True
        ).to_qmark()

        sql = "INSERT INTO [users] ([name]) VALUES ('?'), ('?'), ('?')"
        self.assertEqual(to_sql, sql)
