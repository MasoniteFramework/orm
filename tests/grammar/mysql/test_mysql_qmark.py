from src.masonite.orm.grammar.mysql_grammar import MySQLGrammar 
from src.masonite.orm.builder.QueryBuilder import QueryBuilder
from src.masonite.orm.grammar.GrammarFactory import GrammarFactory
import unittest
import inspect

class BaseQMarkTest:

    def setUp(self):
        self.builder = QueryBuilder(GrammarFactory.make('mysql'), table='users')

    def test_can_compile_select(self):
        mark = self.builder.select('username').where('name', 'Joe').set_action('select')

        sql, bindings = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(mark.to_qmark(), sql)
        self.assertEqual(mark._bindings, bindings)

    def test_can_compile_update(self):
        mark = self.builder.update({
            'name': 'Bob'
        }).where('name', 'Joe')

        sql, bindings = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(mark.to_qmark(), sql)
        self.assertEqual(mark._bindings, bindings)

class TestMySQLQmark(BaseQMarkTest, unittest.TestCase):

    def can_compile_select(self):
        """
        self.builder.select('username').where('name', 'Joe').set_action('select')
        """
        return "SELECT `username` FROM `users` WHERE `name` = '?'", ('Joe',)

    def can_compile_update(self):
        """
        self.builder.update({
            'name': 'Bob'
        }).where('name', 'Joe')
        """
        return "UPDATE `users` SET `name` = '?' WHERE `name` = '?'", ('Bob','Joe',)
