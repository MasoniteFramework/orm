from src.masonite.orm.grammer.mysql_grammer import MySQLGrammer 
import unittest

class TestMySQLUpdateGrammer(unittest.TestCase):


    def test_can_compile_update(self):

        to_sql = MySQLGrammer().create({
            'name': 'Joe'
        })._compile_insert().to_sql()

        sql = "INSERT INTO `users` (`name`) VALUES ('Joe')"
        self.assertEqual(to_sql, sql)
