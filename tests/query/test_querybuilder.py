import unittest

from src.masoniteorm.query import QueryBuilder
from tests.integrations.config.database import DATABASES
from tests.utils import MockSQLiteConnection


class TestQueryBuilder(unittest.TestCase):
    maxDiff = None

    def get_builder(self):
        return QueryBuilder(
            connection="dev",
            connection_class=MockSQLiteConnection,
            connection_details=DATABASES,
        )

    def test_returned_connection_is_same(self):
        builder = self.get_builder()
        first_connection = builder.get_connection()
        self.assertIsNotNone(first_connection)
        second_connection = builder.get_connection()
        self.assertIsNotNone(second_connection)
        self.assertEqual(first_connection, second_connection)

    def test_new_connection_does_not_change_existing_connection(self):
        builder = self.get_builder()
        first_connection = builder.get_connection()
        self.assertIsNotNone(first_connection)
        new_connection = builder.new_connection()
        self.assertIsNotNone(new_connection)
        second_connection = builder.get_connection()
        self.assertIsNotNone(second_connection)
        self.assertEqual(first_connection, second_connection)
        self.assertNotEqual(new_connection, first_connection)
