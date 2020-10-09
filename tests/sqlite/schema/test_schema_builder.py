import unittest
from config.database import DATABASES
from src.masoniteorm.schema import Schema
from src.masoniteorm.connections import SQLiteConnection
from src.masoniteorm.schema.platforms import SQLitePlatform


class TestSQLiteSchemaBuilder(unittest.TestCase):
    def setUp(self):
        self.schema = Schema(
            connection=SQLiteConnection,
            connection_details=DATABASES,
            platform=SQLitePlatform,
            dry=True,
        ).on("sqlite")

    def test_can_add_column(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.integer("age")

        self.assertEqual(len(blueprint.table.added_columns), 2)
        self.assertEqual(
            blueprint.to_sql(), 'CREATE TABLE "users" (name VARCHAR(255), age INTEGER)'
        )
