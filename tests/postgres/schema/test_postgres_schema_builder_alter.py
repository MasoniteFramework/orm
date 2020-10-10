import unittest
from config.database import DATABASES
from src.masoniteorm.schema import Schema
from src.masoniteorm.connections import PostgresConnection
from src.masoniteorm.schema.platforms import PostgresPlatform
from src.masoniteorm.schema.Table import Table


class TestSQLiteSchemaBuilderAlter(unittest.TestCase):
    maxDiff = None

    def setUp(self):

        self.schema = Schema(
            connection=PostgresConnection,
            connection_details=DATABASES,
            platform=PostgresPlatform,
            dry=True,
        ).on("postgres")

    def test_can_add_columns(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name")
            blueprint.integer("age")

        self.assertEqual(len(blueprint.table.added_columns), 2)

        sql = [
            'ALTER TABLE "users" ADD COLUMN name VARCHAR, ADD COLUMN age INTEGER',
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_rename(self):
        with self.schema.table("users") as blueprint:
            blueprint.rename("post", "comment", "integer")

        table = Table("users")
        table.add_column("post", "integer")
        blueprint.table.from_table = table

        sql = ['ALTER TABLE "users" RENAME COLUMN post TO comment']

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_add_and_rename(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name")
            blueprint.rename("post", "comment", "integer")

        table = Table("users")
        table.add_column("post", "integer")
        blueprint.table.from_table = table

        sql = [
            'ALTER TABLE "users" ADD COLUMN name VARCHAR',
            'ALTER TABLE "users" RENAME COLUMN post TO comment',
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_column("post")

        sql = ['ALTER TABLE "users" DROP COLUMN post']

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop_on_table_schema_table(self):
        schema = Schema(
            connection=PostgresConnection,
            connection_details=DATABASES,
        )

        with schema.table("table_schema") as blueprint:
            blueprint.drop_column("name")

        with schema.table("table_schema") as blueprint:
            blueprint.string("name")
