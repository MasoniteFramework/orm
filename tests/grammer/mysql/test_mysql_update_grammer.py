from src.masonite.orm.grammer.mysql_grammer import MySQLGrammer
from src.masonite.orm.builder.QueryBuilder import QueryBuilder
from src.masonite.orm.grammer.GrammerFactory import GrammerFactory 
import unittest

class TestMySQLUpdateGrammer(unittest.TestCase):


    def setUp(self):
        self.builder = QueryBuilder(GrammerFactory.make('mysql'), table='users')

    def test_can_compile_update(self):

        to_sql = self.builder.where('name', 'bob').update({
            'name': 'Joe'
        }).to_sql()

        sql = "UPDATE `users` SET `name` = 'Joe' WHERE `name` = 'bob'"
        self.assertEqual(to_sql, sql)
