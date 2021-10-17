import inspect
import unittest

from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import MySQLGrammar


class BaseQMarkTest:
    def setUp(self):
        self.builder = QueryBuilder(grammar=MySQLGrammar, table="users")

    def test_can_compile_select(self):
        mark = self.builder.select("username").where("name", "Joe")

        sql, bindings = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(mark.to_qmark(), sql)
        self.assertEqual(mark._bindings, bindings)

    def test_can_compile_delete(self):
        mark = self.builder.where("name", "Joe").delete(query=True)

        sql, bindings = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(mark.to_qmark(), sql)
        self.assertEqual(mark._bindings, bindings)

    def test_can_compile_update(self):
        mark = self.builder.update({"name": "Bob"}, dry=True).where("name", "Joe")

        sql, bindings = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(mark.to_qmark(), sql)
        self.assertEqual(mark._bindings, bindings)

    def test_can_compile_where_in(self):
        mark = self.builder.where_in("id", [1, 2, 3])

        sql, bindings = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(mark.to_qmark(), sql)
        self.assertEqual(mark._bindings, bindings)

    def test_can_compile_where_not_null(self):
        mark = self.builder.where_not_null("id")

        sql, bindings = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(mark.to_qmark(), sql)
        self.assertEqual(mark._bindings, [])

    def test_can_compile_where_with_falsy_values(self):
        mark = self.builder.where("name", 0)

        sql, bindings = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(mark.to_qmark(), sql)
        self.assertEqual(mark._bindings, bindings)

    def test_can_compile_where_with_true_value(self):
        mark = self.builder.where("is_admin", True)

        sql, bindings = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(mark.to_qmark(), sql)
        self.assertEqual(mark._bindings, bindings)

    def test_can_compile_where_with_false_value(self):
        mark = self.builder.where("is_admin", False)

        sql, bindings = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(mark.to_qmark(), sql)
        self.assertEqual(mark._bindings, bindings)


class TestMySQLQmark(BaseQMarkTest, unittest.TestCase):
    def can_compile_select(self):
        """
        self.builder.select('username').where('name', 'Joe')
        """
        return (
            "SELECT `users`.`username` FROM `users` WHERE `users`.`name` = '?'",
            ["Joe"],
        )

    def can_compile_delete(self):
        """
        self.builder.where('name', 'Joe').delete()
        """
        return "DELETE FROM `users` WHERE `users`.`name` = '?'", ["Joe"]

    def can_compile_update(self):
        """
        self.builder.update({
            'name': 'Bob'
        }).where('name', 'Joe')
        """
        return (
            "UPDATE `users` SET `users`.`name` = '?' WHERE `users`.`name` = '?'",
            ["Bob", "Joe"],
        )

    def can_compile_where_in(self):
        """
        self.builder.where_in('id', [1,2,3]).to_qmark()
        """
        return (
            "SELECT * FROM `users` WHERE `users`.`id` IN ('?', '?', '?')",
            ["1", "2", "3"],
        )

    def can_compile_where_not_null(self):
        """
        self.builder.where_not_null("id").to_qmark()
        """
        return ("SELECT * FROM `users` WHERE `users`.`id` IS NOT NULL", ())

    def can_compile_where_with_falsy_values(self):
        """
        self.builder.where_not_null("id").to_qmark()
        """
        return ("SELECT * FROM `users` WHERE `users`.`name` = '?'", [0])

    def can_compile_where_with_true_value(self):
        """
        self.builder.where("is_admin", True).to_qmark()
        """
        return ("SELECT * FROM `users` WHERE `users`.`is_admin` = '1'", [])

    def can_compile_where_with_false_value(self):
        """
        self.builder.where("is_admin", True).to_qmark()
        """
        return ("SELECT * FROM `users` WHERE `users`.`is_admin` = '0'", [])
