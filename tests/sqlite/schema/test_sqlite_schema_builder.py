import unittest

from tests.integrations.config.database import DATABASES
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

    def test_can_add_columns(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.integer("age")

        self.assertEqual(len(blueprint.table.added_columns), 2)
        self.assertEqual(
            blueprint.to_sql(),
            [
                'CREATE TABLE "users" ("name" VARCHAR(255) NOT NULL, "age" INTEGER NOT NULL)'
            ],
        )

    def test_can_create_table_if_not_exists(self):
        with self.schema.create_table_if_not_exists("users") as blueprint:
            blueprint.string("name")
            blueprint.integer("age")

        self.assertEqual(len(blueprint.table.added_columns), 2)
        self.assertEqual(
            blueprint.to_sql(),
            [
                'CREATE TABLE IF NOT EXISTS "users" ("name" VARCHAR(255) NOT NULL, "age" INTEGER NOT NULL)'
            ],
        )

    def test_can_add_columns_with_constraint(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.integer("age")
            blueprint.unique("name")

        self.assertEqual(len(blueprint.table.added_columns), 2)
        self.assertEqual(
            blueprint.to_sql(),
            [
                'CREATE TABLE "users" ("name" VARCHAR(255) NOT NULL, "age" INTEGER NOT NULL, UNIQUE(name))'
            ],
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
            [
                'CREATE TABLE "users" '
                '("name" VARCHAR(255) NOT NULL, '
                '"age" INTEGER NOT NULL, '
                '"profile_id" INTEGER NOT NULL, '
                "UNIQUE(name), "
                'CONSTRAINT users_profile_id_foreign FOREIGN KEY ("profile_id") REFERENCES "profiles"("id"))'
            ],
        )

    def test_can_add_columns_with_foreign_key_constraint_name(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name").unique()
            blueprint.integer("age")
            blueprint.integer("profile_id")
            blueprint.foreign("profile_id", name="profile_foreign").references("id").on(
                "profiles"
            )

        self.assertEqual(len(blueprint.table.added_columns), 3)
        self.assertEqual(
            blueprint.to_sql(),
            [
                'CREATE TABLE "users" '
                '("name" VARCHAR(255) NOT NULL, '
                '"age" INTEGER NOT NULL, '
                '"profile_id" INTEGER NOT NULL, '
                "UNIQUE(name), "
                'CONSTRAINT profile_foreign FOREIGN KEY ("profile_id") REFERENCES "profiles"("id"))'
            ],
        )

    def test_can_use_morphs_for_polymorphism_relationships(self):
        with self.schema.create("likes") as blueprint:
            blueprint.morphs("record")

        self.assertEqual(len(blueprint.table.added_columns), 2)
        sql = [
            'CREATE TABLE "likes" ("record_id" UNSIGNED INT NOT NULL, "record_type" VARCHAR(255) NOT NULL)',
            'CREATE INDEX likes_record_id_index ON "likes"(record_id)',
            'CREATE INDEX likes_record_type_index ON "likes"(record_type)',
        ]
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_advanced_table_creation(self):
        with self.schema.create("users") as blueprint:
            blueprint.increments("id")
            blueprint.string("name")
            blueprint.enum("gender", ["male", "female"])
            blueprint.string("email").unique()
            blueprint.string("password")
            blueprint.string("option").default("ADMIN")
            blueprint.integer("admin").default(0)
            blueprint.string("remember_token").nullable()
            blueprint.timestamp("verified_at").nullable()
            blueprint.unique(["email", "name"])
            blueprint.timestamps()

        self.assertEqual(len(blueprint.table.added_columns), 11)
        self.assertEqual(
            blueprint.to_sql(),
            [
                """CREATE TABLE "users" ("id" INTEGER NOT NULL, "name" VARCHAR(255) NOT NULL, "gender" VARCHAR(255) CHECK(gender IN ('male', 'female')) NOT NULL, "email" VARCHAR(255) NOT NULL, """
                """"password" VARCHAR(255) NOT NULL, "option" VARCHAR(255) NOT NULL DEFAULT 'ADMIN', "admin" INTEGER NOT NULL DEFAULT 0, "remember_token" VARCHAR(255) NULL, """
                '"verified_at" TIMESTAMP NULL, "created_at" DATETIME NULL DEFAULT CURRENT_TIMESTAMP, '
                '"updated_at" DATETIME NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT users_id_primary PRIMARY KEY (id), '
                "UNIQUE(email), UNIQUE(email, name))"
            ],
        )

    def test_can_create_indexes(self):
        with self.schema.table("users") as blueprint:
            blueprint.index("name")
            blueprint.index("active", "active_idx")
            blueprint.index(["name", "email"])
            blueprint.unique("name")
            blueprint.unique(["name", "email"])
            blueprint.fulltext("description")

        self.assertEqual(len(blueprint.table.added_columns), 0)
        self.assertEqual(
            blueprint.to_sql(),
            [
                'CREATE INDEX users_name_index ON "users"(name)',
                'CREATE INDEX active_idx ON "users"(active)',
                'CREATE INDEX users_name_email_index ON "users"(name,email)',
                'CREATE UNIQUE INDEX users_name_unique ON "users"(name)',
                'CREATE UNIQUE INDEX users_name_email_unique ON "users"(name,email)',
            ],
        )

    def test_can_create_indexes_on_previous_column(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("email").index()
            blueprint.string("active").index(name="email_idx")

        self.assertEqual(len(blueprint.table.added_columns), 2)
        self.assertEqual(
            blueprint.to_sql(),
            [
                'ALTER TABLE "users" ADD COLUMN "email" VARCHAR NOT NULL',
                'ALTER TABLE "users" ADD COLUMN "active" VARCHAR NOT NULL',
                'CREATE INDEX users_email_index ON "users"(email)',
                'CREATE INDEX email_idx ON "users"(active)',
            ],
        )

    def test_can_have_composite_keys(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name").unique()
            blueprint.integer("age")
            blueprint.integer("profile_id")
            blueprint.primary(["name", "age"])

        self.assertEqual(len(blueprint.table.added_columns), 3)
        self.assertEqual(
            blueprint.to_sql(),
            [
                'CREATE TABLE "users" '
                '("name" VARCHAR(255) NOT NULL, '
                '"age" INTEGER NOT NULL, '
                '"profile_id" INTEGER NOT NULL, '
                "UNIQUE(name), "
                "CONSTRAINT users_name_age_primary PRIMARY KEY (name, age))"
            ],
        )

    def test_can_have_column_primary_key(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name").primary()
            blueprint.integer("age")
            blueprint.integer("profile_id")

        self.assertEqual(len(blueprint.table.added_columns), 3)
        self.assertEqual(
            blueprint.to_sql(),
            [
                'CREATE TABLE "users" '
                '("name" VARCHAR(255) NOT NULL, '
                '"age" INTEGER NOT NULL, '
                '"profile_id" INTEGER NOT NULL, '
                "CONSTRAINT users_name_primary PRIMARY KEY (name))"
            ],
        )

    def test_can_advanced_table_creation2(self):
        with self.schema.create("users") as blueprint:
            blueprint.big_increments("id")
            blueprint.string("name")
            blueprint.string("duration")
            blueprint.string("url")
            blueprint.json("payload")
            blueprint.year("birth")
            blueprint.inet("last_address").nullable()
            blueprint.cidr("route_origin").nullable()
            blueprint.macaddr("mac_address").nullable()
            blueprint.datetime("published_at")
            blueprint.time("wakeup_at")
            blueprint.string("thumbnail").nullable()
            blueprint.integer("premium")
            blueprint.integer("author_id").unsigned().nullable()
            blueprint.foreign("author_id").references("id").on("users").on_delete(
                "set null"
            )
            blueprint.text("description")
            blueprint.timestamps()

        self.assertEqual(len(blueprint.table.added_columns), 17)

        self.assertEqual(
            blueprint.to_sql(),
            (
                [
                    'CREATE TABLE "users" ("id" BIGINT NOT NULL, "name" VARCHAR(255) NOT NULL, "duration" VARCHAR(255) NOT NULL, '
                    '"url" VARCHAR(255) NOT NULL, "payload" JSON NOT NULL, "birth" VARCHAR(4) NOT NULL, "last_address" VARCHAR(255) NULL, "route_origin" VARCHAR(255) NULL, "mac_address" VARCHAR(255) NULL, '
                    '"published_at" DATETIME NOT NULL, "wakeup_at" TIME NOT NULL, "thumbnail" VARCHAR(255) NULL, "premium" INTEGER NOT NULL, "author_id" UNSIGNED INT NULL, "description" TEXT NOT NULL, '
                    '"created_at" DATETIME NULL DEFAULT CURRENT_TIMESTAMP, "updated_at" DATETIME NULL DEFAULT CURRENT_TIMESTAMP, '
                    'CONSTRAINT users_id_primary PRIMARY KEY (id), CONSTRAINT users_author_id_foreign FOREIGN KEY ("author_id") REFERENCES "users"("id") ON DELETE SET NULL)'
                ]
            ),
        )

    def test_has_table(self):
        schema_sql = self.schema.has_table("users")

        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"

        self.assertEqual(schema_sql, sql)

    def test_can_truncate(self):
        sql = self.schema.truncate("users")

        self.assertEqual(sql, 'DELETE FROM "users"')

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
                'DELETE FROM "users"',
                "PRAGMA foreign_keys = ON",
            ],
        )
