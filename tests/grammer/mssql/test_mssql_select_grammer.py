import unittest
from src.masonite.orm.grammer.mssql_grammer import MSSQLGrammer
from src.masonite.orm.builder.QueryBuilder import QueryBuilder
from src.masonite.orm.grammer.GrammerFactory import GrammerFactory

class TestSQLServerGrammer(unittest.TestCase):

    def setUp(self):
        self.builder = QueryBuilder(GrammerFactory.make('mssql'), table='users')

    def test_can_compile_select(self):
        to_sql = self.builder.set_action('select').to_sql()
        sql = "SELECT * FROM [users]"
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_columns(self):
        to_sql = self.builder.select('username', 'password').set_action('select').to_sql()
        sql = "SELECT [username], [password] FROM [users]"
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_where(self):
        to_sql = self.builder.select('username', 'password').where(
            'id', 1).set_action('select').to_sql()
        sql = "SELECT [username], [password] FROM [users] WHERE [id] = '1'"
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_several_where(self):
        to_sql = self.builder.select('username', 'password').where(
            'id', 1).where('username', 'joe').set_action('select').to_sql()
        sql = "SELECT [username], [password] FROM [users] WHERE [id] = '1' AND [username] = 'joe'"
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_several_where_and_limit(self):
        to_sql = self.builder.select('username', 'password').where(
            'id', 1).where('username', 'joe').limit(10).set_action('select').to_sql()
        sql = "SELECT TOP 10 [username], [password] FROM [users] WHERE [id] = '1' AND [username] = 'joe'"
        self.assertEqual(to_sql, sql)
