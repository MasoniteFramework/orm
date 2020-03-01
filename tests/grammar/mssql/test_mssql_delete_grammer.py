from src.masonite.orm.grammar.mysql_grammar import MySQLGrammar
from src.masonite.orm.builder.QueryBuilder import QueryBuilder
from src.masonite.orm.grammar.GrammarFactory import GrammarFactory
import unittest


class TestMySQLDeleteGrammar(unittest.TestCase):
    def setUp(self):
        self.builder = QueryBuilder(GrammarFactory.make("mssql"), table="users")

    def test_can_compile_delete(self):
        to_sql = self.builder.delete("id", 1).to_sql()

        sql = "DELETE FROM [users] WHERE [id] = '1'"
        self.assertEqual(to_sql, sql)

    def test_can_compile_delete_with_where(self):
        to_sql = (
            self.builder.where("age", 20)
            .where("profile", 1)
            .set_action("delete")
            .delete()
            .to_sql()
        )

        sql = "DELETE FROM [users] WHERE [age] = '20' AND [profile] = '1'"
        self.assertEqual(to_sql, sql)
