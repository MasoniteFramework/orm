import unittest

from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import MSSQLGrammar


class TestMSSQLQmark(unittest.TestCase):
    def setUp(self):
        self.builder = QueryBuilder(MSSQLGrammar, table="users")

    def test_can_compile_select(self):
        mark = self.builder.select("username").where("name", "Joe")

        sql = "SELECT [users].[username] FROM [users] WHERE [users].[name] = '?'"
        self.assertEqual(mark.to_qmark(), sql)
        self.assertEqual(mark._bindings, ["Joe"])

    def test_can_compile_update(self):
        mark = self.builder.update({"name": "Bob"}, dry=True).where("name", "Joe")

        sql = "UPDATE [users] SET [users].[name] = '?' WHERE [users].[name] = '?'"
        self.assertEqual(mark.to_qmark(), sql)
        self.assertEqual(mark._bindings, ["Bob", "Joe"])

    def test_can_compile_insert(self):
        mark = self.builder.create({"name": "Bob"}, query=True)

        sql = "INSERT INTO [users] ([users].[name]) VALUES ('?')"
        self.assertEqual(mark.to_qmark(), sql)
        self.assertEqual(mark._bindings, ["Bob"])

    def test_can_compile_where_in(self):
        mark = self.builder.where_in("id", [1, 2, 3])

        sql = "SELECT * FROM [users] WHERE [users].[id] IN ('?', '?', '?')"
        self.assertEqual(mark.to_qmark(), sql)
        self.assertEqual(mark._bindings, ["1", "2", "3"])
