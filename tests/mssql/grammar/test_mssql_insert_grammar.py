from src.masoniteorm.query.grammars import MySQLGrammar
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import GrammarFactory
import unittest


class TestMySQLInsertGrammar(unittest.TestCase):
    def setUp(self):
        self.builder = QueryBuilder(GrammarFactory.make("mssql"), table="users")

    def test_can_compile_insert(self):

        to_sql = self.builder.create({"name": "Joe"}, query=True).to_sql()

        sql = "INSERT INTO [users] ([users].[name]) VALUES ('Joe')"
        self.assertEqual(to_sql, sql)
