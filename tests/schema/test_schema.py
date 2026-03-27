import unittest

from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import SQLitePlatform
from tests.integrations.config.database import DATABASES
from tests.utils import MockSQLiteConnection


class TestSchema(unittest.TestCase):
    maxDiff = None

    def get_schema(self):
        return Schema(
            connection="dev",
            connection_class=MockSQLiteConnection,
            connection_details=DATABASES,
            platform=SQLitePlatform,
        )

    def test_connection_is_cached(self):
        schema = self.get_schema()
        first_connection = schema.get_connection()
        self.assertIsNotNone(first_connection)
        second_connection = schema.get_connection()
        self.assertIsNotNone(second_connection)
        self.assertEqual(first_connection, second_connection)

    def test_new_connection_is_not_cached(self):
        schema = self.get_schema()
        first_connection = schema.get_connection()
        self.assertIsNotNone(first_connection)
        new_connection = schema.new_connection()
        self.assertIsNotNone(new_connection)
        second_connection = schema.get_connection()
        self.assertIsNotNone(second_connection)
        self.assertEqual(first_connection, second_connection)
        self.assertNotEqual(new_connection, first_connection)

    def test_can_get_query_builder(self):
        schema = self.get_schema()
        builder = schema.query_builder()
        self.assertIsInstance(builder, QueryBuilder)
