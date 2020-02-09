from src.masonite.orm.grammar.mysql_grammar import MySQLGrammar 
from src.masonite.orm.builder.QueryBuilder import QueryBuilder
from src.masonite.orm.grammar.GrammarFactory import GrammarFactory
import unittest

class TestMySQLUpdateGrammar(unittest.TestCase):

    def setUp(self):
        self.builder = QueryBuilder(GrammarFactory.make('mysql'), table='users')

    def test_can_compile_insert(self):

        to_sql = self.builder.create({
            'name': 'Joe'
        }).to_sql()

        sql = "INSERT INTO `users` (`name`) VALUES ('Joe')"
        self.assertEqual(to_sql, sql)
