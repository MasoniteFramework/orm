import unittest

from tests.integrations.config.database import DATABASES
from src.masoniteorm.connections import SQLiteConnection
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import SQLitePlatform
from src.masoniteorm.schema.Table import Table


class TestSQLiteSchemaBuilderAlter(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.schema = Schema(
            connection="dev",
            connection_details=DATABASES,
            platform=SQLitePlatform,
            dry=True,
        ).on("dev")

    def test_can_add_columns(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name")
            blueprint.string("external_type").default("external")
            blueprint.integer("age")

        self.assertEqual(len(blueprint.table.added_columns), 3)

        sql = [
            'ALTER TABLE "users" ADD COLUMN "name" VARCHAR NOT NULL',
            """ALTER TABLE "users" ADD COLUMN "external_type" VARCHAR NOT NULL DEFAULT 'external'""",
            'ALTER TABLE "users" ADD COLUMN "age" INTEGER NOT NULL',
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_add_constraints(self):
        with self.schema.table("users") as blueprint:
            blueprint.unique("name", name="table_unique")

        self.assertEqual(len(blueprint.table.added_columns), 0)

        sql = ['CREATE UNIQUE INDEX table_unique ON "users"(name)']

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_rename(self):
        with self.schema.table("users") as blueprint:
            blueprint.rename("post", "comment", "integer")

        table = Table("users")
        table.add_column("post", "integer")
        blueprint.table.from_table = table

        sql = [
            "CREATE TEMPORARY TABLE __temp__users AS SELECT post FROM users",
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("comment" INTEGER NOT NULL)',
            'INSERT INTO "users" ("comment") SELECT post FROM __temp__users',
            "DROP TABLE __temp__users",
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_column("post")

        table = Table("users")
        table.add_column("post", "string")
        table.add_column("name", "string")
        table.add_column("email", "string")
        blueprint.table.from_table = table

        sql = [
            "CREATE TEMPORARY TABLE __temp__users AS SELECT name, email FROM users",
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("name" VARCHAR NOT NULL, "email" VARCHAR NOT NULL)',
            'INSERT INTO "users" ("name", "email") SELECT name, email FROM __temp__users',
            "DROP TABLE __temp__users",
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_change(self):
        with self.schema.table("users") as blueprint:
            blueprint.integer("age").change()
            blueprint.string("name")

        self.assertEqual(len(blueprint.table.added_columns), 1)
        self.assertEqual(len(blueprint.table.changed_columns), 1)
        table = Table("users")
        table.add_column("age", "string")

        blueprint.table.from_table = table

        sql = [
            'ALTER TABLE "users" ADD COLUMN "name" VARCHAR NOT NULL',
            "CREATE TEMPORARY TABLE __temp__users AS SELECT age FROM users",
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("age" INTEGER NOT NULL, "name" VARCHAR(255) NOT NULL)',
            'INSERT INTO "users" ("age") SELECT age FROM __temp__users',
            "DROP TABLE __temp__users",
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_drop_add_and_change(self):
        with self.schema.table("users") as blueprint:
            blueprint.integer("age").change()
            blueprint.string("name")
            blueprint.drop_column("email")

        self.assertEqual(len(blueprint.table.added_columns), 1)
        self.assertEqual(len(blueprint.table.changed_columns), 1)
        table = Table("users")
        table.add_column("age", "string")
        table.add_column("email", "string")

        blueprint.table.from_table = table

        sql = [
            'ALTER TABLE "users" ADD COLUMN "name" VARCHAR',
            "CREATE TEMPORARY TABLE __temp__users AS SELECT age FROM users",
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("age" INTEGER NOT NULL, "name" VARCHAR(255) NOT NULL)',
            'INSERT INTO "users" ("age") SELECT age FROM __temp__users',
            "DROP TABLE __temp__users",
        ]

    def test_timestamp_alter_add_nullable_column(self):
        with self.schema.table("users") as blueprint:
            blueprint.timestamp("due_date").nullable()

        self.assertEqual(len(blueprint.table.added_columns), 1)

        table = Table("users")
        table.add_column("age", "string")

        blueprint.table.from_table = table

        sql = ['ALTER TABLE "users" ADD COLUMN "due_date" TIMESTAMP NULL']

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop_on_table_schema_table(self):
        schema = Schema(connection="dev", connection_details=DATABASES).on("dev")

        with schema.table("table_schema") as blueprint:
            blueprint.drop_column("name")

        with schema.table("table_schema") as blueprint:
            blueprint.string("name").nullable()

    def test_alter_add_primary(self):
        with self.schema.table("users") as blueprint:
            blueprint.primary("playlist_id")

        sql = [
            'ALTER TABLE "users" ADD CONSTRAINT users_playlist_id_primary PRIMARY KEY (playlist_id)'
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_add_column_and_foreign_key(self):
        with self.schema.table("users") as blueprint:
            blueprint.unsigned_integer("playlist_id").nullable()
            blueprint.foreign("playlist_id").references("id").on("playlists").on_delete(
                "cascade"
            ).on_update("SET NULL")

        table = Table("users")
        table.add_column("age", "string")
        table.add_column("email", "string")

        blueprint.table.from_table = table

        sql = [
            'ALTER TABLE "users" ADD COLUMN "playlist_id" UNSIGNED INT NULL REFERENCES "playlists"("id")',
            "CREATE TEMPORARY TABLE __temp__users AS SELECT age, email FROM users",
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("age" VARCHAR NOT NULL, "email" VARCHAR NOT NULL, "playlist_id" UNSIGNED INT NULL, '
            'CONSTRAINT users_playlist_id_foreign FOREIGN KEY ("playlist_id") REFERENCES "playlists"("id") ON DELETE CASCADE ON UPDATE SET NULL)',
            'INSERT INTO "users" ("age", "email") SELECT age, email FROM __temp__users',
            "DROP TABLE __temp__users",
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_add_foreign_key_only(self):
        with self.schema.table("users") as blueprint:
            blueprint.foreign("playlist_id").references("id").on("playlists").on_delete(
                "cascade"
            ).on_update("set null")

        table = Table("users")
        table.add_column("age", "string")
        table.add_column("email", "string")

        blueprint.table.from_table = table

        sql = [
            "CREATE TEMPORARY TABLE __temp__users AS SELECT age, email FROM users",
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("age" VARCHAR NOT NULL, "email" VARCHAR NOT NULL, '
            'CONSTRAINT users_playlist_id_foreign FOREIGN KEY ("playlist_id") REFERENCES "playlists"("id") ON DELETE CASCADE ON UPDATE SET NULL)',
            'INSERT INTO "users" ("age", "email") SELECT age, email FROM __temp__users',
            "DROP TABLE __temp__users",
        ]

        self.assertEqual(blueprint.to_sql(), sql)
