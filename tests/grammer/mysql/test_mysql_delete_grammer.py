from src.masonite.orm.grammer.mysql_grammer import MySQLGrammer 
import unittest

class TestMySQLUpdateGrammer(unittest.TestCase):


    def test_can_compile_update(self):

        to_sql = (
            MySQLGrammer()
            .delete('id', 1)
            ._compile_delete()
            .to_sql()
        )

        sql = "DELETE FROM `users` WHERE `id` = '1'"
        self.assertEqual(to_sql, sql)
