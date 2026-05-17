import unittest

from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import MSSQLGrammar


class TestMSSQLQmark(unittest.TestCase):
    def setUp(self):
        self.builder = QueryBuilder(MSSQLGrammar, table="users")

    def test_can_compile_select(self):
        mark = self.builder.select("username").where("name", "Joe")
        query_sql = mark.to_qmark()
        expected_sql = (
            "SELECT [users].[username] FROM [users] WHERE [users].[name] = ?"
        )
        self.assertEqual(query_sql, expected_sql)
        self.assertEqual(mark._bindings, ["Joe"])

    def test_can_compile_update(self):
        mark = self.builder.update({"name": "Bob"}, dry=True).where(
            "name", "Joe"
        )
        query_sql = mark.to_qmark()
        expected_sql = (
            "UPDATE [users] SET [users].[name] = ? WHERE [users].[name] = ?"
        )
        self.assertEqual(query_sql, expected_sql)
        self.assertEqual(mark._bindings, ["Bob", "Joe"])

    def test_can_compile_insert(self):
        mark = self.builder.create({"name": "Bob"}, query=True)
        query_sql = mark.to_qmark()
        expected_sql = "INSERT INTO [users] ([users].[name]) VALUES (?)"
        self.assertEqual(query_sql, expected_sql)
        self.assertEqual(mark._bindings, ["Bob"])

    def test_can_compile_where_in(self):
        mark = self.builder.where_in("id", [1, 2, 3])
        query_sql = mark.to_qmark()
        expected_sql = "SELECT * FROM [users] WHERE [users].[id] IN (?, ?, ?)"
        self.assertEqual(query_sql, expected_sql)
        self.assertEqual(mark._bindings, [1, 2, 3])
        # to_sql uses quoted values, not placeholders
        query_sql = self.builder.where_in("id", [1, 2, 3]).to_sql()
        expected_sql = (
            "SELECT * FROM [users] WHERE [users].[id] IN ('1','2','3')"
        )
        self.assertEqual(query_sql, expected_sql)
        self.builder.reset()
        # String values should produce the same quoted SQL
        query_sql = self.builder.where_in("id", ["1", "2", "3"]).to_sql()
        expected_sql = (
            "SELECT * FROM [users] WHERE [users].[id] IN ('1','2','3')"
        )
        self.assertEqual(query_sql, expected_sql)
