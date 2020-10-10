import unittest
from config.database import DATABASES
from src.masoniteorm.schema import Schema
from src.masoniteorm.connections import MySQLConnection
from src.masoniteorm.schema.platforms import MySQLPlatform


class TestMySQLSchemaBuilder(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.schema = Schema(
            connection=MySQLConnection,
            connection_details=DATABASES,
            platform=MySQLPlatform,
            dry=True,
        ).on("sqlite")

    def test_can_add_columns1(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.integer("age")

        self.assertEqual(len(blueprint.table.added_columns), 2)
        self.assertEqual(
            blueprint.to_sql(), "CREATE TABLE users (name VARCHAR(255), age INT(11))"
        )

    def test_can_add_columns_with_constaint(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.integer("age")
            blueprint.unique("name")

        self.assertEqual(len(blueprint.table.added_columns), 2)
        self.assertEqual(
            blueprint.to_sql(),
            "CREATE TABLE users (name VARCHAR(255), age INT(11), CONSTRAINT users_name_unique UNIQUE (name))",
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
            "CREATE TABLE users (name VARCHAR(255), "
            "age INT(11), "
            "profile_id INT(11), "
            "CONSTRAINT users_name_unique UNIQUE (name), "
            "CONSTRAINT profile_id_users_profiles_id_foreign FOREIGN KEY (profile_id) REFERENCES profiles(id))",
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
                "CREATE TABLE users (id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, "
                "name VARCHAR(255), email VARCHAR(255), password VARCHAR(255), "
                "admin INT(11), remember_token VARCHAR(255), verified_at TIMESTAMP, "
                "created_at TIMESTAMP, updated_at TIMESTAMP, CONSTRAINT users_email_unique UNIQUE (email))"
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
            blueprint.foreign("author_id").references("id").on("users").on_delete(
                "CASCADE"
            )
            blueprint.text("description")
            blueprint.timestamps()

        self.assertEqual(len(blueprint.table.added_columns), 11)
        self.assertEqual(
            blueprint.to_sql(),
            (
                "CREATE TABLE users (id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), "
                "duration VARCHAR(255), url VARCHAR(255), published_at DATETIME, thumbnail VARCHAR(255), "
                "premium INT(11), author_id INT UNSIGNED, description TEXT, created_at TIMESTAMP, "
                "updated_at TIMESTAMP, CONSTRAINT author_id_users_users_id_foreign FOREIGN KEY (author_id) REFERENCES users(id))"
            ),
        )
