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

    def test_can_compile_update_with_multiple_where(self):
        to_sql = self.builder.where('name', 'bob').where('age', 20).update({
            'name': 'Joe'
        }).to_sql()

        sql = "UPDATE `users` SET `name` = 'Joe' WHERE `name` = 'bob' AND `age` = '20'"
        self.assertEqual(to_sql, sql)
