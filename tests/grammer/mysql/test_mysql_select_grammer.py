from src.masonite.orm.grammer.mysql_grammer import MySQLGrammer 
from src.masonite.orm.grammer.GrammerFactory import GrammerFactory
from src.masonite.orm.builder.QueryBuilder import QueryBuilder
import unittest

class TestMySQLGrammer(unittest.TestCase):

    def setUp(self):
        self.builder = QueryBuilder(GrammerFactory.make('mysql'), table='users')

    def test_can_compile_select(self):
        to_sql = self.builder.to_sql()
        sql = "SELECT * FROM `users`"
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_columns(self):
        to_sql = self.builder.select('username', 'password').to_sql()
        sql = "SELECT `username`, `password` FROM `users`"
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_where(self):
        to_sql = self.builder.select('username', 'password').where('id', 1).to_sql()
        sql = "SELECT `username`, `password` FROM `users` WHERE `id` = '1'"
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_several_where(self):
        to_sql = self.builder.select('username', 'password').where('id', 1).where('username', 'joe').to_sql()
        sql = "SELECT `username`, `password` FROM `users` WHERE `id` = '1' AND `username` = 'joe'"
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_several_where_and_limit(self):
        to_sql = self.builder.select('username', 'password').where('id', 1).where('username', 'joe').limit(10).to_sql()
        sql = "SELECT `username`, `password` FROM `users` WHERE `id` = '1' AND `username` = 'joe' LIMIT 10"
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_sum(self):
        to_sql = self.builder.sum('age').to_sql()
        sql = "SELECT SUM(`age`) as age FROM `users`"
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_max(self):
        to_sql = self.builder.max('age').to_sql()
        sql = "SELECT MAX(`age`) AS age FROM `users`"
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_max_and_columns(self):
        to_sql = self.builder.select('username').max('age').to_sql()
        sql = "SELECT `username`, MAX(`age`) AS age FROM `users`"
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_max_and_columns_different_order(self):
        to_sql = self.builder.max('age').select('username').to_sql()
        sql = "SELECT `username`, MAX(`age`) AS age FROM `users`"
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_order_by(self):
        to_sql = self.builder.select('username').order_by('age', 'desc').to_sql()
        sql = "SELECT `username` FROM `users` ORDER BY `age` DESC"
        self.assertEqual(to_sql, sql)


