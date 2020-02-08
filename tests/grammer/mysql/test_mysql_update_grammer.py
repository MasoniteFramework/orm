from src.masonite.orm.grammer.mysql_grammer import MySQLGrammer 
import unittest

class TestMySQLUpdateGrammer(unittest.TestCase):


    def test_can_compile_update(self):

        to_sql = MySQLGrammer().where('name', 'bob').update({
            'name': 'Joe'
        })._compile_update().to_sql()

        sql = "UPDATE `users` SET `name` = 'Joe' WHERE `name` = 'bob'"
        self.assertEqual(to_sql, sql)
