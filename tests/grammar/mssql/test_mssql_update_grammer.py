from src.masonite.orm.grammar.mysql_grammar import MySQLGrammar
from src.masonite.orm.builder.QueryBuilder import QueryBuilder
from src.masonite.orm.grammar.GrammarFactory import GrammarFactory 
import unittest

class TestMySQLUpdateGrammar(unittest.TestCase):


    def setUp(self):
        self.builder = QueryBuilder(GrammarFactory.make('mssql'), table='users')

    def test_can_compile_update(self):

        to_sql = self.builder.where('name', 'bob').update({
            'name': 'Joe'
        }).to_sql()

        sql = "UPDATE [users] SET [name] = 'Joe' WHERE [name] = 'bob'"
        self.assertEqual(to_sql, sql)

    def test_can_compile_update_with_multiple_where(self):
        to_sql = self.builder.where('name', 'bob').where('age', 20).update({
            'name': 'Joe'
        }).to_sql()

        sql = "UPDATE [users] SET [name] = 'Joe' WHERE [name] = 'bob' AND [age] = '20'"
        self.assertEqual(to_sql, sql)
