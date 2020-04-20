from src.masonite.orm.grammar.mysql_grammar import MySQLGrammar
from src.masonite.orm.builder import QueryBuilder
from src.masonite.orm.grammar import GrammarFactory
import unittest
import inspect


class BaseInsertGrammarTest:
    def setUp(self):
        self.builder = QueryBuilder(GrammarFactory.make(self.grammar), table="users")

    def test_can_compile_insert(self):

        to_sql = self.builder.create({"name": "Joe"}, query=True).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)


class TestMySQLUpdateGrammar(BaseInsertGrammarTest, unittest.TestCase):

    grammar = "mysql"

    def can_compile_insert(self):
        """
        self.builder.create({
            'name': 'Joe'
        }).to_sql()
        """
        return "INSERT INTO `users` (`users`.`name`) VALUES ('Joe')"
