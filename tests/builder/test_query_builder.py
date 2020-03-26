import inspect
import unittest

from src.masonite.orm.builder import QueryBuilder
from src.masonite.orm.models import Model
from src.masonite.orm.grammar import MySQLGrammar
from tests.utils import MockConnectionFactory


class BaseTestQueryBuilder:
    def get_builder(self, table="users"):
        connection = MockConnectionFactory().make("default")
        return QueryBuilder(
            self.grammar,
            connection,
            table=table,
            owner=Model
        )

    def test_sum(self):
        builder = self.get_builder()
        builder.sum('age')

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_max(self):
        builder = self.get_builder()
        builder.max('age')

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_min(self):
        builder = self.get_builder()
        builder.min('age')

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_avg(self):
        builder = self.get_builder()
        builder.avg('age')
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_all(self):
        builder = self.get_builder()
        builder.all()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_get(self):
        builder = self.get_builder()
        builder.get()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    # def test_first(self):
    #     builder = self.get_builder()
    #     builder.first()
    #     print(builder.to_sql())
    #     sql = getattr(
    #         self, inspect.currentframe().f_code.co_name.replace("test_", "")
    #     )()
    #     self.assertEqual(builder.to_sql(), sql)


class MySQLQueryBuilderTest(BaseTestQueryBuilder, unittest.TestCase):
    grammar = MySQLGrammar

    def sum(self):
        """
            builder = self.get_builder()
            builder.sum('age')
        """
        return 'SELECT SUM(`age`) AS age FROM `users`'

    def max(self):
        """
            builder = self.get_builder()
            builder.max('age')
        """
        return "SELECT MAX(`age`) AS age FROM `users`"

    def min(self):
        """
            builder = self.get_builder()
            builder.min('age')
        """
        return "SELECT MIN(`age`) AS age FROM `users`"

    def avg(self):
        """
            builder = self.get_builder()
            builder.avg('age')
        """
        return "SELECT AVG(`age`) AS age FROM `users`"

    def first(self):
        """
            builder = self.get_builder()
            builder.first()
        """
        return "SELECT * FROM `users` LIMIT 1"

    def all(self):
        """
            builder = self.get_builder()
            builder.all()
        """
        return "SELECT * FROM `users`"

    def get(self):
        """
            builder = self.get_builder()
            builder.get()
        """
        return "SELECT * FROM `users`"

