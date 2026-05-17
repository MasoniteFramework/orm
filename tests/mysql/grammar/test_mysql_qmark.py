import unittest

from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import MySQLGrammar


class TestMySQLQmark(unittest.TestCase):
    def setUp(self):
        self.builder = QueryBuilder(grammar=MySQLGrammar, table="users")

    def test_can_compile_select(self):
        mark = self.builder.select("username").where("name", "Joe")
        query_sql = mark.to_qmark()
        expected_sql = (
            "SELECT `users`.`username` FROM `users` WHERE `users`.`name` = ?"
        )
        self.assertEqual(query_sql, expected_sql)
        self.assertEqual(mark._bindings, ["Joe"])

    def test_can_compile_delete(self):
        mark = self.builder.where("name", "Joe").delete(query=True)
        query_sql = mark.to_qmark()
        expected_sql = "DELETE FROM `users` WHERE `users`.`name` = ?"
        self.assertEqual(query_sql, expected_sql)
        self.assertEqual(mark._bindings, ["Joe"])

    def test_can_compile_update(self):
        mark = self.builder.update({"name": "Bob"}, dry=True).where(
            "name", "Joe"
        )
        query_sql = mark.to_qmark()
        expected_sql = (
            "UPDATE `users` SET `users`.`name` = ? WHERE `users`.`name` = ?"
        )
        self.assertEqual(query_sql, expected_sql)
        self.assertEqual(mark._bindings, ["Bob", "Joe"])

    def test_can_compile_where_in(self):
        mark = self.builder.where_in("id", [1, 2, 3])
        query_sql = mark.to_qmark()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`id` IN (?, ?, ?)"
        self.assertEqual(query_sql, expected_sql)
        self.assertEqual(mark._bindings, [1, 2, 3])

    def test_can_compile_where_not_null(self):
        mark = self.builder.where_not_null("id")
        query_sql = mark.to_qmark()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`id` IS NOT NULL"
        self.assertEqual(query_sql, expected_sql)
        self.assertEqual(mark._bindings, [])

    def test_can_compile_where_with_falsy_values(self):
        mark = self.builder.where("name", 0)
        query_sql = mark.to_qmark()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`name` = ?"
        self.assertEqual(query_sql, expected_sql)
        self.assertEqual(mark._bindings, [0])

    def test_can_compile_where_with_true_value(self):
        mark = self.builder.where("is_admin", True)
        query_sql = mark.to_qmark()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`is_admin` = '1'"
        self.assertEqual(query_sql, expected_sql)
        self.assertEqual(mark._bindings, [])

    def test_can_compile_where_with_false_value(self):
        mark = self.builder.where("is_admin", False)
        query_sql = mark.to_qmark()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`is_admin` = '0'"
        self.assertEqual(query_sql, expected_sql)
        self.assertEqual(mark._bindings, [])

    def test_can_compile_sub_group_bindings(self):
        mark = self.builder.where(
            lambda query: query.where("challenger", 1)
            .or_where("proposer", 1)
            .or_where("referee", 1)
        )
        query_sql = mark.to_qmark()
        expected_sql = "SELECT * FROM `users` WHERE (`users`.`challenger` = ? OR `users`.`proposer` = ? OR `users`.`referee` = ?)"
        self.assertEqual(query_sql, expected_sql)
        self.assertEqual(mark._bindings, [1, 1, 1])

    def test_can_increment(self):
        builder = self.builder.increment("age", dry=True)
        query_sql = builder.to_qmark()
        expected_sql = "UPDATE `users` SET `users`.`age` = `users`.`age` + ?"
        self.assertEqual(query_sql, expected_sql)
        self.assertEqual(builder._bindings, [1])

    def test_can_decrement(self):
        builder = self.builder.decrement("age", dry=True)
        query_sql = builder.to_qmark()
        expected_sql = "UPDATE `users` SET `users`.`age` = `users`.`age` - ?"
        self.assertEqual(query_sql, expected_sql)
        self.assertEqual(builder._bindings, [1])
