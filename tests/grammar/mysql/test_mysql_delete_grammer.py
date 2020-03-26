from src.masonite.orm.grammar.mysql_grammar import MySQLGrammar
from src.masonite.orm.builder import QueryBuilder
from src.masonite.orm.grammar import GrammarFactory
import unittest, inspect


class BaseDeleteGrammarTest:
    def setUp(self):
        self.builder = QueryBuilder(GrammarFactory.make(self.grammar), table="users")

    def test_can_compile_delete(self):
        to_sql = self.builder.delete("id", 1).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_delete_in(self):
        to_sql = self.builder.delete("id", [1, 2, 3]).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_delete_with_where(self):
        to_sql = (
            self.builder.where("age", 20)
            .where("profile", 1)
            .set_action("delete")
            .delete()
            .to_sql()
        )

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)


class TestMySQLDeleteGrammar(BaseDeleteGrammarTest, unittest.TestCase):

    grammar = "mysql"

    def can_compile_delete(self):
        """
        (
            self.builder
            .delete('id', 1)
            .to_sql()
        )
        """
        return "DELETE FROM `users` WHERE `id` = '1'"

    def can_compile_delete_in(self):
        """
        (
            self.builder
            .delete('id', 1)
            .to_sql()
        )
        """
        return "DELETE FROM `users` WHERE `id` IN ('1','2','3')"

    def can_compile_delete_with_where(self):
        """
        (
            self.builder
            .where('age', 20)
            .where('profile', 1)
            .set_action('delete')
            .delete()
            .to_sql()
        )
        """
        return "DELETE FROM `users` WHERE `age` = '20' AND `profile` = '1'"
