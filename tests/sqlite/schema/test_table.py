import unittest

from tests.integrations.config.database import DATABASES
from src.masoniteorm.connections import SQLiteConnection
from src.masoniteorm.schema import Column, Table
from src.masoniteorm.schema.platforms.SQLitePlatform import SQLitePlatform


class TestTable(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.platform = SQLitePlatform()

    def test_add_columns(self):
        table = Table("users")
        table.add_column("name", "string")

        self.assertIsInstance(table.added_columns["name"], Column)

    def test_primary_key(self):
        table = Table("users")
        table.add_column("id", "integer")
        table.set_primary_key("id")

        self.assertEqual(table.primary_key, "id")

    def test_create_sql(self):
        table = Table("users")
        table.add_column("id", "integer")
        table.add_column("name", "string")

        sql = 'CREATE TABLE "users" ("id" INTEGER NOT NULL, "name" VARCHAR NOT NULL)'
        self.assertEqual([sql], self.platform.compile_create_sql(table))

    def test_create_sql_with_primary_key(self):
        table = Table("users")
        table.add_column("id", "integer")
        table.add_column("name", "string")
        table.set_primary_key("id")

        sql = 'CREATE TABLE "users" ("id" INTEGER NOT NULL, "name" VARCHAR NOT NULL)'
        self.assertEqual([sql], self.platform.compile_create_sql(table))

    def test_create_sql_with_unique_constraint(self):
        table = Table("users")
        table.add_column("id", "integer")
        table.add_column("name", "string")
        table.add_constraint("name", "unique", ["name"])
        table.set_primary_key("id")

        sql = 'CREATE TABLE "users" ("id" INTEGER NOT NULL, "name" VARCHAR NOT NULL, UNIQUE(name))'
        self.platform.constraintize(table.get_added_constraints())
        self.assertEqual(self.platform.compile_create_sql(table), [sql])

    def test_create_sql_with_multiple_unique_constraints(self):
        table = Table("users")
        table.add_column("id", "integer")
        table.add_column("email", "string")
        table.add_column("name", "string")
        table.add_constraint("name", "unique", ["name"])
        table.add_constraint("email", "unique", ["email"])
        table.set_primary_key("id")

        sql = 'CREATE TABLE "users" ("id" INTEGER NOT NULL, "email" VARCHAR NOT NULL, "name" VARCHAR NOT NULL, UNIQUE(name), UNIQUE(email))'
        self.platform.constraintize(table.get_added_constraints())
        self.assertEqual(self.platform.compile_create_sql(table), [sql])

    def test_create_sql_with_multiple_unique_constraint(self):
        table = Table("users")
        table.add_column("id", "integer")
        table.add_column("email", "string")
        table.add_column("name", "string")
        table.add_constraint("name", "unique", ["name", "email"])
        table.set_primary_key("id")

        sql = 'CREATE TABLE "users" ("id" INTEGER NOT NULL, "email" VARCHAR NOT NULL, "name" VARCHAR NOT NULL, UNIQUE(name, email))'
        self.platform.constraintize(table.get_added_constraints())
        self.assertEqual(self.platform.compile_create_sql(table), [sql])

    def test_create_sql_with_foreign_key_constraint(self):
        table = Table("users")
        table.add_column("id", "integer")
        table.add_column("profile_id", "integer")
        table.add_column("comment_id", "integer")
        table.add_foreign_key("profile_id", "profiles", "id")
        table.add_foreign_key("comment_id", "comments", "id")
        table.set_primary_key("id")

        sql = (
            'CREATE TABLE "users" ('
            '"id" INTEGER NOT NULL, "profile_id" INTEGER NOT NULL, "comment_id" INTEGER NOT NULL, '
            'CONSTRAINT users_profile_id_foreign FOREIGN KEY ("profile_id") REFERENCES "profiles"("id"), '
            'CONSTRAINT users_comment_id_foreign FOREIGN KEY ("comment_id") REFERENCES "comments"("id"))'
        )

        self.platform.constraintize(table.get_added_constraints())
        self.assertEqual(self.platform.compile_create_sql(table), [sql])

    def test_can_build_table_from_connection_call(self):
        sql_details = DATABASES["dev"]
        table = self.platform.get_current_schema(
            SQLiteConnection(
                database=sql_details["database"], name="dev"
            ).make_connection(),
            "table_schema",
        )

        self.assertEqual(len(table.added_columns), 4)
