from src.masoniteorm.orm.builder import QueryBuilder
from src.masoniteorm.orm.grammar import GrammarFactory, MySQLGrammar
import unittest
import inspect


class BaseInsertGrammarTest:
    def setUp(self):
        self.builder = QueryBuilder(GrammarFactory.make(self.grammar), table="users")

    def test_can_compile_insert(self):
        to_sql = self.builder.create({"name": "Joe"}, query=True).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_insert_with_keywords(self):
        to_sql = self.builder.create(name="Joe", query=True).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)


class TestMySQLUpdateGrammar(BaseInsertGrammarTest, unittest.TestCase):

    grammar = "mysql"

    def can_compile_insert(self):
        """
        self.builder.create({
            'name': 'Joe'
        }).to_sql()
        """
        return "INSERT INTO `users` (`users`.`name`) VALUES ('Joe')"

    def can_compile_insert_with_keywords(self):
        """
        self.builder.create(name="Joe").to_sql()
        """
        return "INSERT INTO `users` (`users`.`name`) VALUES ('Joe')"
