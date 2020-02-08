import unittest
from src.masonite.orm.grammer.mssql_grammer import MSSQLGrammer

class TestSQLServerGrammer(unittest.TestCase):

    def test_can_compile_select(self):
        to_sql = MSSQLGrammer()._compile_select().to_sql()
        sql = "SELECT * FROM [users]"
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_columns(self):
        to_sql = MSSQLGrammer().select('username', 'password')._compile_select().to_sql()
        sql = "SELECT [username], [password] FROM [users]"
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_where(self):
        to_sql = MSSQLGrammer().select('username', 'password').where(
            'id', 1)._compile_select().to_sql()
        sql = "SELECT [username], [password] FROM [users] WHERE [id] = '1'"
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_several_where(self):
        to_sql = MSSQLGrammer().select('username', 'password').where(
            'id', 1).where('username', 'joe')._compile_select().to_sql()
        sql = "SELECT [username], [password] FROM [users] WHERE [id] = '1' AND [username] = 'joe'"
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_several_where_and_limit(self):
        to_sql = MSSQLGrammer().select('username', 'password').where(
            'id', 1).where('username', 'joe').limit(10)._compile_select().to_sql()
        sql = "SELECT TOP 10 [username], [password] FROM [users] WHERE [id] = '1' AND [username] = 'joe'"
        self.assertEqual(to_sql, sql)
