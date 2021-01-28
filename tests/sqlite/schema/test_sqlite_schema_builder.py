import unittest

from config.database import DATABASES
from src.masoniteorm.connections import SQLiteConnection
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import SQLitePlatform


class TestSQLiteSchemaBuilder(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.schema = Schema(
            connection="dev",
            connection_details=DATABASES,
            platform=SQLitePlatform,
            dry=True,
        ).on("dev")

        self.schema_database = Schema(
            connection_class=SQLiteConnection,
            connection="dev",
            connection_details=DATABASES,
            platform=SQLitePlatform,
        ).on("dev")

    def tearDown(self):
        self.schema_database.drop_table_if_exists("users")

    def test_can_add_columns(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.integer("age")

        self.assertEqual(len(blueprint.table.added_columns), 2)
        self.assertEqual(
            blueprint.to_sql(),
            'CREATE TABLE "users" (name VARCHAR(255) NOT NULL, age INTEGER NOT NULL)',
        )

    def test_can_add_columns_with_constraint(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.integer("age")
            blueprint.unique("name")

        self.assertEqual(len(blueprint.table.added_columns), 2)
        self.assertEqual(
            blueprint.to_sql(),
            'CREATE TABLE "users" (name VARCHAR(255) NOT NULL, age INTEGER NOT NULL, UNIQUE(name))',
        )

    def test_can_add_columns_with_foreign_key_constraint(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name").unique()
            blueprint.integer("age")
            blueprint.integer("profile_id")
            blueprint.foreign("profile_id").references("id").on("profiles")

        self.assertEqual(len(blueprint.table.added_columns), 3)
        self.assertEqual(
            blueprint.to_sql(),
            'CREATE TABLE "users" '
            "(name VARCHAR(255) NOT NULL, "
            "age INTEGER NOT NULL, "
            "profile_id INTEGER NOT NULL, "
            "UNIQUE(name), "
            "CONSTRAINT users_profile_id_foreign FOREIGN KEY (profile_id) REFERENCES profiles(id))",
        )

    def test_can_use_morphs_for_polymorphism_relationships(self):
        with self.schema.create("likes") as blueprint:
            blueprint.morphs("record")

        self.assertEqual(len(blueprint.table.added_columns), 2)
        self.assertEqual(
            blueprint.to_sql(),
            'CREATE TABLE "likes" '
            "(record_id UNSIGNED INT NOT NULL, "
            "record_type VARCHAR NOT NULL)",
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
                'CREATE TABLE "users" (id INTEGER PRIMARY KEY NOT NULL, name VARCHAR(255) NOT NULL, email VARCHAR(255) NOT NULL, '
                "password VARCHAR(255) NOT NULL, admin INTEGER NOT NULL DEFAULT 0, remember_token VARCHAR(255) NULL, "
                "verified_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP, created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP, "
                "updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(email))"
            ),
        )

    def test_can_advanced_table_creation2(self):
        with self.schema.create("users") as blueprint:
            blueprint.increments("id")
            blueprint.string("name")
            blueprint.string("duration")
            blueprint.string("url")
            blueprint.json("payload")
            blueprint.year("birth")
            blueprint.datetime("published_at")
            blueprint.time("wakeup_at")
            blueprint.string("thumbnail").nullable()
            blueprint.integer("premium")
            blueprint.integer("author_id").unsigned().nullable()
            blueprint.foreign("author_id").references("id").on("users").on_delete(
                "CASCADE"
            )
            blueprint.text("description")
            blueprint.timestamps()

        self.assertEqual(len(blueprint.table.added_columns), 14)

        print(blueprint.to_sql())
        self.assertEqual(
            blueprint.to_sql(),
            (
                'CREATE TABLE "users" (id INTEGER PRIMARY KEY NOT NULL, name VARCHAR(255) NOT NULL, duration VARCHAR(255) NOT NULL, '
                "url VARCHAR(255) NOT NULL, payload JSON NOT NULL, birth VARCHAR(4) NOT NULL, published_at DATETIME NOT NULL, wakeup_at TIME NOT NULL, thumbnail VARCHAR(255) NULL, premium INTEGER NOT NULL, "
                "author_id UNSIGNED INT NULL, description TEXT NOT NULL, created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP, "
                "updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP, "
                "CONSTRAINT users_author_id_foreign FOREIGN KEY (author_id) REFERENCES users(id))"
            ),
        )

    def test_has_table(self):
        schema_sql = self.schema.has_table("users")

        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"

        self.assertEqual(schema_sql, sql)

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

    def test_can_enable_foreign_keys(self):
        sql = self.schema.enable_foreign_key_constraints()

        self.assertEqual(sql, "PRAGMA foreign_keys = ON")

    def test_can_disable_foreign_keys(self):
        sql = self.schema.disable_foreign_key_constraints()

        self.assertEqual(sql, "PRAGMA foreign_keys = OFF")

    def test_can_truncate_without_foreign_keys(self):
        sql = self.schema.truncate("users", foreign_keys=True)

        self.assertEqual(
            sql,
            [
                "PRAGMA foreign_keys = OFF",
                'TRUNCATE "users"',
                "PRAGMA foreign_keys = ON",
            ],
        )

    def test_return_correct_columns_from_table(self):

        with self.schema_database.create("users") as blueprint:
            blueprint.increments("id")
            blueprint.string("name", 100)
            blueprint.string("email")
            blueprint.string("password")
            blueprint.string("remember_token", 150)
            blueprint.timestamps()
            blueprint.timestamp("verified_at")
            blueprint.boolean("is_active").default(True)

        columns = self.schema_database.list_table_columns("users")

        self.assertEqual("id: integer default: None", columns[0])
        self.assertEqual("name: string(100) default: None", columns[1])
        self.assertEqual("email: string(255) default: None", columns[2])
        self.assertEqual("password: string(255) default: None", columns[3])
        self.assertEqual("remember_token: string(150) default: None", columns[4])
        self.assertEqual("created_at: timestamp default: CURRENT_TIMESTAMP", columns[5])
        self.assertEqual("updated_at: timestamp default: CURRENT_TIMESTAMP", columns[6])
        self.assertEqual(
            "verified_at: timestamp default: CURRENT_TIMESTAMP", columns[7]
        )
        self.assertEqual("is_active: boolean default: True", columns[8])
