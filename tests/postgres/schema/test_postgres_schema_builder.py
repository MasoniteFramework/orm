import unittest

from tests.integrations.config.database import DATABASES
from src.masoniteorm.connections import PostgresConnection
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import PostgresPlatform


class TestPostgresSchemaBuilder(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.schema = Schema(
            connection_class=PostgresConnection,
            connection="postgres",
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

    def test_can_add_column_comment(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name").comment("A users username")

        self.assertEqual(len(blueprint.table.added_columns), 1)
        self.assertEqual(
            blueprint.to_sql(),
            [
                'CREATE TABLE "users" ("name" VARCHAR(255) NOT NULL)',
                """COMMENT ON COLUMN "users"."name" is 'A users username'""",
            ],
        )

    def test_can_add_table_comment(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.table_comment("A users table")

        self.assertEqual(len(blueprint.table.added_columns), 1)
        self.assertEqual(
            blueprint.to_sql(),
            [
                'CREATE TABLE "users" ("name" VARCHAR(255) NOT NULL)',
                """COMMENT ON TABLE "users" is 'A users table'""",
            ],
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
            [
                'CREATE TABLE "users" ("name" VARCHAR(255) NOT NULL, "age" INTEGER NOT NULL, CONSTRAINT users_name_unique UNIQUE (name))'
            ],
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
            [
                'CREATE TABLE "users" ("name" VARCHAR(255) NOT NULL, "age" INTEGER NOT NULL, '
                '"profile_id" INTEGER NOT NULL, CONSTRAINT users_name_unique UNIQUE (name), '
                'CONSTRAINT users_profile_id_foreign FOREIGN KEY ("profile_id") REFERENCES "profiles"("id"))'
            ],
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
            [
                'CREATE TABLE "users" ("id" SERIAL UNIQUE NOT NULL, "name" VARCHAR(255) NOT NULL, '
                '"email" VARCHAR(255) NOT NULL, "password" VARCHAR(255) NOT NULL, "admin" INTEGER NOT NULL DEFAULT 0, '
                '"remember_token" VARCHAR(255) NULL, "verified_at" TIMESTAMP NULL, '
                '"created_at" TIMESTAMPTZ NULL DEFAULT CURRENT_TIMESTAMP, "updated_at" TIMESTAMPTZ NULL DEFAULT CURRENT_TIMESTAMP, '
                "CONSTRAINT users_id_primary PRIMARY KEY (id), CONSTRAINT users_email_unique UNIQUE (email))"
            ],
        )

    def test_can_advanced_table_creation2(self):
        with self.schema.create("users") as blueprint:
            blueprint.big_increments("id")
            blueprint.string("name")
            blueprint.enum("gender", ["male", "female"])
            blueprint.string("duration")
            blueprint.decimal("money")
            blueprint.string("url")
            blueprint.string("option").default("ADMIN")
            blueprint.jsonb("payload")
            blueprint.inet("last_address").nullable()
            blueprint.cidr("route_origin").nullable()
            blueprint.macaddr("mac_address").nullable()
            blueprint.datetime("published_at")
            blueprint.string("thumbnail").nullable()
            blueprint.integer("premium")
            blueprint.double("amount").default(0.0)
            blueprint.integer("author_id").unsigned().nullable()
            blueprint.foreign("author_id").references("id").on("authors").on_delete(
                "CASCADE"
            )
            blueprint.text("description")
            blueprint.timestamps()

        self.assertEqual(len(blueprint.table.added_columns), 19)
        self.assertEqual(
            blueprint.to_sql(),
            (
                [
                    """CREATE TABLE "users" ("id" BIGSERIAL UNIQUE NOT NULL, "name" VARCHAR(255) NOT NULL, "gender" VARCHAR(255) CHECK(gender IN ('male', 'female')) NOT NULL, """
                    """"duration" VARCHAR(255) NOT NULL, "money" DECIMAL(17, 6) NOT NULL, "url" VARCHAR(255) NOT NULL, "option" VARCHAR(255) NOT NULL DEFAULT 'ADMIN', "payload" JSONB NOT NULL, "last_address" INET NULL, """
                    '"route_origin" CIDR NULL, "mac_address" MACADDR NULL, "published_at" TIMESTAMPTZ NOT NULL, "thumbnail" VARCHAR(255) NULL, "premium" INTEGER NOT NULL, "amount" DOUBLE PRECISION NOT NULL DEFAULT 0.0, '
                    '"author_id" INT NULL, "description" TEXT NOT NULL, "created_at" TIMESTAMPTZ NULL DEFAULT CURRENT_TIMESTAMP, '
                    '"updated_at" TIMESTAMPTZ NULL DEFAULT CURRENT_TIMESTAMP, '
                    'CONSTRAINT users_id_primary PRIMARY KEY (id), CONSTRAINT users_author_id_foreign FOREIGN KEY ("author_id") REFERENCES "authors"("id") ON DELETE CASCADE)'
                ]
            ),
        )

    def test_can_add_uuid_column(self):
        # might not be the right place for this test + other column types
        # are not tested => just for testing the PR now
        with self.schema.create("users") as table:
            table.uuid("id").default_raw("uuid_generate_v4()")
            table.primary("id")
            table.string("name")
            table.uuid("public_id").nullable()
            table.uuid("other_id").default_raw("uuid_generate_v4()")

        self.assertEqual(len(table.table.added_columns), 4)
        self.assertEqual(
            table.to_sql(),
            [
                'CREATE TABLE "users" ("id" UUID NOT NULL DEFAULT uuid_generate_v4(), "name" VARCHAR(255) NOT NULL, "public_id" UUID NULL, "other_id" UUID NOT NULL DEFAULT uuid_generate_v4(), CONSTRAINT users_id_primary PRIMARY KEY (id))'
            ],
        )

    def test_can_add_columns_with_foreign_key_constraint_name(self):
        with self.schema.create("users") as blueprint:
            blueprint.integer("profile_id")
            blueprint.foreign("profile_id", name="profile_foreign").references("id").on(
                "profiles"
            )

        self.assertEqual(len(blueprint.table.added_columns), 1)
        self.assertEqual(
            blueprint.to_sql(),
            [
                'CREATE TABLE "users" ('
                '"profile_id" INTEGER NOT NULL, '
                'CONSTRAINT profile_foreign FOREIGN KEY ("profile_id") REFERENCES "profiles"("id"))'
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
                "CONSTRAINT users_name_unique UNIQUE (name), "
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

    def test_can_add_other_integer_types_column(self):
        with self.schema.create("integer_types") as table:
            table.tiny_integer("tiny")
            table.small_integer("small")
            table.medium_integer("medium")
            table.big_integer("big")

        self.assertEqual(len(table.table.added_columns), 4)
        self.assertEqual(
            table.to_sql(),
            [
                'CREATE TABLE "integer_types" ("tiny" TINYINT NOT NULL, "small" SMALLINT NOT NULL, "medium" MEDIUMINT NOT NULL, "big" BIGINT NOT NULL)'
            ],
        )

    def test_can_add_binary_column(self):
        with self.schema.create("binary_storing") as table:
            table.binary("filecontent")

        self.assertEqual(len(table.table.added_columns), 1)
        self.assertEqual(
            table.to_sql(),
            ['CREATE TABLE "binary_storing" ("filecontent" BYTEA NOT NULL)'],
        )

    def test_can_enable_foreign_keys(self):
        sql = self.schema.enable_foreign_key_constraints()

        self.assertEqual(sql, "")

    def test_can_disable_foreign_keys(self):
        sql = self.schema.disable_foreign_key_constraints()

        self.assertEqual(sql, "")

    def test_can_truncate_without_foreign_keys(self):
        sql = self.schema.truncate("users", foreign_keys=True)

        self.assertEqual(
            sql,
            [
                'ALTER TABLE "users" DISABLE TRIGGER ALL',
                'TRUNCATE "users"',
                'ALTER TABLE "users" ENABLE TRIGGER ALL',
            ],
        )
