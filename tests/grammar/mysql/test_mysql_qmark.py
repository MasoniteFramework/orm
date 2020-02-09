from src.masonite.orm.grammar.mysql_grammar import MySQLGrammar 
from src.masonite.orm.builder.QueryBuilder import QueryBuilder
from src.masonite.orm.grammar.GrammarFactory import GrammarFactory
import unittest

class TestMySQLQmark(unittest.TestCase):

    def setUp(self):
        self.builder = QueryBuilder(GrammarFactory.make('mysql'), table='users')

    def test_can_compile_select(self):

        mark = self.builder.select('username').where('name', 'Joe').set_action('select')

        sql = "SELECT `username` FROM `users` WHERE `name` = '?'"
        self.assertEqual(mark.to_qmark(), sql)
        self.assertEqual(mark._bindings, ('Joe',))

    def test_can_compile_update(self):
        mark = self.builder.update({
            'name': 'Bob'
        }).where('name', 'Joe')

        sql = "UPDATE `users` SET `name` = '?' WHERE `name` = '?'"
        self.assertEqual(mark.to_qmark(), sql)
        self.assertEqual(mark._bindings, ('Bob','Joe',))
