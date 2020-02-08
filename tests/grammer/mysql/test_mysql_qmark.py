from src.masonite.orm.grammer.mysql_grammer import MySQLGrammer 
from src.masonite.orm.builder.QueryBuilder import QueryBuilder
from src.masonite.orm.grammer.GrammerFactory import GrammerFactory
import unittest

class TestMySQLQmark(unittest.TestCase):

    def setUp(self):
        self.builder = QueryBuilder(GrammerFactory.make('mysql'), table='users')

    def test_can_compile_select(self):

        mark = self.builder.select('username').where('name', 'Joe')

        sql = "SELECT `username` FROM `users` WHERE `name` = '?'"
        self.assertEqual(mark.to_qmark(), sql)
        self.assertEqual(mark._bindings, ('Joe',))
