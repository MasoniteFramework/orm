import unittest

from src.masoniteorm.expressions import Raw
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import MySQLGrammar


class TestMySQLUpdateGrammar(unittest.TestCase):
    def setUp(self):
        self.builder = QueryBuilder(MySQLGrammar, table="users")

    def test_can_compile_update(self):
        query_sql = (
            self.builder.where("name", "bob")
            .update({"name": "Joe"}, dry=True)
            .to_sql()
        )
        expected_sql = "UPDATE `users` SET `users`.`name` = 'Joe' WHERE `users`.`name` = 'bob'"
        self.assertEqual(query_sql, expected_sql)

    def test_raw_expression(self):
        query_sql = self.builder.update(
            {"name": Raw("`username`")}, dry=True
        ).to_sql()
        expected_sql = "UPDATE `users` SET `users`.`name` = `username`"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_multiple_update(self):
        query_sql = self.builder.update(
            {"name": "Joe", "email": "user@email.com"}, dry=True
        ).to_sql()
        expected_sql = "UPDATE `users` SET `users`.`name` = 'Joe', `users`.`email` = 'user@email.com'"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_update_with_multiple_where(self):
        query_sql = (
            self.builder.where("name", "bob")
            .where("age", 20)
            .update({"name": "Joe"}, dry=True)
            .to_sql()
        )
        expected_sql = "UPDATE `users` SET `users`.`name` = 'Joe' WHERE `users`.`name` = 'bob' AND `users`.`age` = '20'"
        self.assertEqual(query_sql, expected_sql)
