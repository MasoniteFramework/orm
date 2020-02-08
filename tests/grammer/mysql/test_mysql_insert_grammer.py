from src.masonite.orm.grammer.mysql_grammer import MySQLGrammer 
from src.masonite.orm.builder.QueryBuilder import QueryBuilder
from src.masonite.orm.grammer.GrammerFactory import GrammerFactory
import unittest

class TestMySQLUpdateGrammer(unittest.TestCase):

    def setUp(self):
        self.builder = QueryBuilder(GrammerFactory.make('mysql'), table='users')

    def test_can_compile_update(self):

        to_sql = self.builder.create({
            'name': 'Joe'
        }).to_sql()

        sql = "INSERT INTO `users` (`name`) VALUES ('Joe')"
        self.assertEqual(to_sql, sql)
