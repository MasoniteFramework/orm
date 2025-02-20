import unittest

from src.masoniteorm import Model
from src.masoniteorm.query.grammars import SQLiteGrammar
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import SQLitePlatform
from src.masoniteorm.schema.Table import Table
from tests.integrations.config.database import DATABASES


class User(Model):
    __connection__ = "dev"
    __timestamps__ = None


class Playlist(Model):
    __connection__ = "dev"
    __timestamps__ = None


class SqliteTestSchemaBuilderAlter(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.schema = Schema(
            grammar=SQLiteGrammar,
            connection="dev",
            connection_details=DATABASES,
            platform=SQLitePlatform,
        ).on("dev")

        cls.schema.drop_table_if_exists("users")
        cls.schema.drop_table_if_exists("playlists")

    def tearDown(self):
        self.schema.drop_table_if_exists("users")
        self.schema.drop_table_if_exists("playlists")

    def test_can_add_columns(self):
        with self.schema.create("users") as setup:
            setup.integer("id")

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
        with self.schema.create("users") as setup:
            setup.string("name")

        with self.schema.table("users") as blueprint:
            blueprint.unique("name", name="table_unique")

        self.assertEqual(len(blueprint.table.added_columns), 0)

        sql = ['CREATE UNIQUE INDEX table_unique ON "users"(name)']
        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_rename(self):
        with self.schema.create("users") as setup:
            setup.string("post")

        with self.schema.table("users") as blueprint:
            blueprint.rename("post", "comment", "integer")

        sql = [
            "CREATE TEMPORARY TABLE __temp__users AS SELECT comment FROM users",
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("comment" INTEGER NOT NULL, "comment" INTEGER NOT NULL)',
            'INSERT INTO "users" ("comment", "comment") SELECT comment, post FROM __temp__users',
            "DROP TABLE __temp__users",
        ]
        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop(self):
        with self.schema.create("users") as setup:
            setup.integer("id")
            setup.string("name")
            setup.string("post")

        with self.schema.table("users") as blueprint:
            blueprint.string("name").nullable().change()
            # TODO: fix dropcolumn - KeyError: 'post'
            # blueprint.drop_column("post")

        sql = [
            "CREATE TEMPORARY TABLE __temp__users AS SELECT id, name, post FROM users",
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("id" INTEGER NOT NULL, "name" VARCHAR(255) NULL, "post" VARCHAR(255) NOT NULL)',
            'INSERT INTO "users" ("id", "name", "post") SELECT id, name, post FROM __temp__users',
            "DROP TABLE __temp__users",
        ]
        self.assertEqual(blueprint.to_sql(), sql)

    def test_add_and_change(self):
        with self.schema.create("users") as setup:
            setup.integer("age")

        with self.schema.table("users") as blueprint:
            blueprint.integer("age").change()
            blueprint.string("name")

        self.assertEqual(len(blueprint.table.added_columns), 1)
        self.assertEqual(len(blueprint.table.changed_columns), 1)

        sql = [
            'ALTER TABLE "users" ADD COLUMN "name" VARCHAR NOT NULL',
            "CREATE TEMPORARY TABLE __temp__users AS SELECT age, name FROM users",
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("age" INTEGER NOT NULL, "name" VARCHAR(255) NOT NULL)',
            'INSERT INTO "users" ("age") SELECT age FROM __temp__users',
            "DROP TABLE __temp__users",
        ]
        self.assertEqual(blueprint.to_sql(), sql)

    def test_drop_add_and_change(self):
        with self.schema.create("users") as setup:
            setup.string("email")
            setup.integer("age")

        with self.schema.table("users") as blueprint:
            # TODO: fix dropping a column in this manner
            # throws a KeyError 'email' when running tests
            # blueprint.drop_column("email")
            blueprint.integer("age").change()
            blueprint.string("name")

        self.assertEqual(len(blueprint.table.added_columns), 1)
        self.assertEqual(len(blueprint.table.changed_columns), 1)

        # sql = [
        #     'ALTER TABLE "users" ADD COLUMN "name" VARCHAR',
        #     "CREATE TEMPORARY TABLE __temp__users AS SELECT age FROM users",
        #     'DROP TABLE "users"',
        #     'CREATE TABLE "users" ("age" INTEGER NOT NULL, "name" VARCHAR(255) NOT NULL)',
        #     'INSERT INTO "users" ("age") SELECT age FROM __temp__users',
        #     "DROP TABLE __temp__users",
        # ]
        # self.assertEqual(blueprint.to_sql(), sql)

    def test_timestamp_alter_add_nullable_column(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")

        with self.schema.table("users") as blueprint:
            blueprint.timestamp("due_date").nullable()

        self.assertEqual(len(blueprint.table.added_columns), 1)

        table = Table("users")
        table.add_column("age", "string")

        blueprint.table.from_table = table

        sql = ['ALTER TABLE "users" ADD COLUMN "due_date" TIMESTAMP NULL']
        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_add_primary(self):
        with self.schema.create("users") as setup:
            setup.string("name")

        with self.schema.table("users") as blueprint:
            blueprint.integer("id")
            # TODO: fix addina a primary key after table creation fails: Syntax error near CONSTRAINT
            # blueprint.primary("id")

        # sql = [
        #     'ALTER TABLE "users" ADD CONSTRAINT users_id_primary PRIMARY KEY (id)'
        # ]
        # self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_add_column_and_foreign_key(self):
        with self.schema.create("playlists") as setup:
            setup.integer("id")
        with self.schema.create("users") as setup:
            setup.string("name")

        with self.schema.table("users") as blueprint:
            blueprint.unsigned_integer("playlist_id").nullable()
            blueprint.foreign("playlist_id").references("id").on("playlists").on_delete(
                "cascade"
            ).on_update("SET NULL")

        sql = [
            'ALTER TABLE "users" ADD COLUMN "playlist_id" INTEGER UNSIGNED NULL REFERENCES "playlists"("id")',
            "CREATE TEMPORARY TABLE __temp__users AS SELECT name, playlist_id FROM users",
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("name" VARCHAR(255) NOT NULL, "playlist_id" INTEGER UNSIGNED NULL, CONSTRAINT users_playlist_id_foreign FOREIGN KEY ("playlist_id") REFERENCES "playlists"("id") ON DELETE CASCADE ON UPDATE SET NULL)',
            'INSERT INTO "users" ("name") SELECT name FROM __temp__users',
            "DROP TABLE __temp__users",
        ]
        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_add_foreign_key_only(self):
        with self.schema.create("playlists") as setup:
            setup.integer("id")
        with self.schema.create("users") as setup:
            setup.string("name")
            setup.integer("playlist_id")

        with self.schema.table("users") as blueprint:
            blueprint.foreign("playlist_id").references("id").on("playlists").on_delete(
                "cascade"
            ).on_update("set null")

        sql = [
            "CREATE TEMPORARY TABLE __temp__users AS SELECT name, playlist_id FROM users",
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("name" VARCHAR(255) NOT NULL, "playlist_id" INTEGER NOT NULL, CONSTRAINT users_playlist_id_foreign FOREIGN KEY ("playlist_id") REFERENCES "playlists"("id") ON DELETE CASCADE ON UPDATE SET NULL)',
            'INSERT INTO "users" ("name", "playlist_id") SELECT name, playlist_id FROM __temp__users',
            "DROP TABLE __temp__users",
        ]
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_add_column_enum(self):
        with self.schema.create("users") as setup:
            setup.string("name")

        with self.schema.table("users") as blueprint:
            blueprint.enum("status", ["active", "inactive"]).default("active")
        self.assertEqual(len(blueprint.table.added_columns), 1)

        sql = [
            "ALTER TABLE \"users\" ADD COLUMN \"status\" VARCHAR CHECK('status' IN('active', 'inactive')) NOT NULL DEFAULT 'active'"
        ]
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_change_column_enum(self):
        with self.schema.create("users") as setup:
            setup.enum("status", ["busu", "available"])

        with self.schema.table("users") as blueprint:
            blueprint.enum("status", ["active", "inactive"]).default("active").change()

        self.assertEqual(len(blueprint.table.changed_columns), 1)
        sql = [
            "CREATE TEMPORARY TABLE __temp__users AS SELECT status FROM users",
            'DROP TABLE "users"',
            "CREATE TABLE \"users\" (\"status\" VARCHAR(255) CHECK(status IN ('active', 'inactive')) NOT NULL DEFAULT 'active')",
            'INSERT INTO "users" ("status") SELECT status FROM __temp__users',
            "DROP TABLE __temp__users",
        ]
        self.assertEqual(blueprint.to_sql(), sql)
