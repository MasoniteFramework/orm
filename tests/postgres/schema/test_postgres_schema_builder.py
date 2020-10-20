import unittest

from config.database import DATABASES
from src.masoniteorm.connections import PostgresConnection
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import PostgresPlatform


class TestPostgresSchemaBuilder(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.schema = Schema(
            connection=PostgresConnection,
            connection_details=DATABASES,
            platform=PostgresPlatform,
            dry=True,
        )

    def test_can_add_columns(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.integer("age")

        self.assertEqual(len(blueprint.table.added_columns), 2)
        self.assertEqual(
            blueprint.to_sql(),
            'CREATE TABLE "users" (name VARCHAR(255) NOT NULL, age INTEGER NOT NULL)',
        )

    def test_can_truncate(self):
        sql = self.schema.truncate("users")

        self.assertEqual(sql, 'TRUNCATE "users"')

    def test_can_rename_table(self):
        sql = self.schema.rename("users", "clients")

        self.assertEqual(sql, 'ALTER TABLE "users" RENAME TO "clients"')

    def test_can_drop_table_if_exists(self):
        sql = self.schema.drop_table_if_exists("users", "clients")

        self.assertEqual(sql, 'DROP TABLE IF EXISTS "users"')

    def test_can_drop_table(self):
        sql = self.schema.drop_table("users", "clients")

        self.assertEqual(sql, 'DROP TABLE "users"')

    def test_has_column(self):
        sql = self.schema.has_column("users", "name")

        self.assertEqual(
            sql,
            "SELECT column_name FROM information_schema.columns WHERE table_name='users' and column_name='name'",
        )

    def test_can_add_columns_with_constaint(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.integer("age")
            blueprint.unique("name")

        self.assertEqual(len(blueprint.table.added_columns), 2)
        self.assertEqual(
            blueprint.to_sql(),
            'CREATE TABLE "users" (name VARCHAR(255) NOT NULL, age INTEGER NOT NULL, CONSTRAINT users_name_unique UNIQUE (name))',
        )

    def test_can_add_columns_with_foreign_key_constaint(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name").unique()
            blueprint.integer("age")
            blueprint.integer("profile_id")
            blueprint.foreign("profile_id").references("id").on("profiles")

        self.assertEqual(len(blueprint.table.added_columns), 3)
        self.assertEqual(
            blueprint.to_sql(),
            'CREATE TABLE "users" (name VARCHAR(255) NOT NULL, age INTEGER NOT NULL, '
            "profile_id INTEGER NOT NULL, CONSTRAINT users_name_unique UNIQUE (name), "
            "CONSTRAINT users_profile_id_foreign FOREIGN KEY (profile_id) REFERENCES profiles(id))",
        )

    def test_can_advanced_table_creation(self):
        with self.schema.create("users") as blueprint:
            blueprint.increments("id")
            blueprint.string("name")
            blueprint.string("email").unique()
            blueprint.string("password")
            blueprint.integer("admin").default(0)
            blueprint.string("remember_token").nullable()
            blueprint.timestamp("verified_at").nullable()
            blueprint.timestamps()

        self.assertEqual(len(blueprint.table.added_columns), 9)
        self.assertEqual(
            blueprint.to_sql(),
            (
                'CREATE TABLE "users" (id SERIAL UNIQUE NOT NULL, name VARCHAR(255) NOT NULL, '
                "email VARCHAR(255) NOT NULL, password VARCHAR(255) NOT NULL, admin INTEGER NOT NULL DEFAULT 0, "
                "remember_token VARCHAR(255) NULL, verified_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP, "
                "created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP, "
                "CONSTRAINT users_email_unique UNIQUE (email))"
            ),
        )

    def test_can_advanced_table_creation2(self):
        with self.schema.create("users") as blueprint:
            blueprint.increments("id")
            blueprint.string("name")
            blueprint.string("duration")
            blueprint.string("url")
            blueprint.datetime("published_at")
            blueprint.string("thumbnail").nullable()
            blueprint.integer("premium")
            blueprint.integer("author_id").unsigned().nullable()
            blueprint.foreign("author_id").references("id").on("authors").on_delete(
                "CASCADE"
            )
            blueprint.text("description")
            blueprint.timestamps()

        self.assertEqual(len(blueprint.table.added_columns), 11)
        self.assertEqual(
            blueprint.to_sql(),
            (
                'CREATE TABLE "users" (id SERIAL UNIQUE NOT NULL, name VARCHAR(255) NOT NULL, '
                "duration VARCHAR(255) NOT NULL, url VARCHAR(255) NOT NULL, published_at TIMESTAMP NOT NULL, "
                "thumbnail VARCHAR(255) NULL, premium INTEGER NOT NULL, author_id INT NULL, "
                "description TEXT NOT NULL, created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP, "
                "updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP, "
                "CONSTRAINT users_author_id_foreign FOREIGN KEY (author_id) REFERENCES authors(id))"
            ),
        )

    def test_can_add_uuid_column(self):
        # might not be the right place for this test + other column types
        # are not tested => just for testing the PR now
        with self.schema.create("users") as table:
            table.uuid("id")
            table.primary("id")
            table.string("name")
            table.uuid("public_id").nullable()

        self.assertEqual(len(table.table.added_columns), 3)
        self.assertEqual(
            table.to_sql(),
            'CREATE TABLE "users" (id CHAR(36) NOT NULL PRIMARY KEY, name VARCHAR(255) NOT NULL, public_id CHAR(36) NULL)',
        )
