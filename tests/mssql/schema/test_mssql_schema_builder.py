import unittest

from tests.integrations.config.database import DATABASES
from src.masoniteorm.connections import MSSQLConnection
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import MSSQLPlatform


class TestMSSQLSchemaBuilder(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.schema = Schema(
            connection_class=MSSQLConnection,
            connection="mssql",
            connection_details=DATABASES,
            platform=MSSQLPlatform,
            dry=True,
        ).on("mssql")

    def test_can_add_columns(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.integer("age")

        self.assertEqual(len(blueprint.table.added_columns), 2)
        self.assertEqual(
            blueprint.to_sql(),
            ["CREATE TABLE [users] ([name] VARCHAR(255) NOT NULL, [age] INT NOT NULL)"],
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
                "CREATE TABLE [users] ([name] VARCHAR(255) NOT NULL, [age] INT NOT NULL, CONSTRAINT users_name_unique UNIQUE (name))"
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
                "CREATE TABLE [users] "
                "([name] VARCHAR(255) NOT NULL, "
                "[age] INT NOT NULL, "
                "[profile_id] INT NOT NULL, "
                "CONSTRAINT users_name_unique UNIQUE (name), "
                "CONSTRAINT users_profile_id_foreign FOREIGN KEY ([profile_id]) REFERENCES [profiles]([id]))"
            ],
        )

    def test_can_add_columns_with_add_foreign_constaint(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name").unique()
            blueprint.integer("age")
            blueprint.integer("profile_id")
            blueprint.add_foreign("profile_id.id.profiles")

        self.assertEqual(len(blueprint.table.added_columns), 3)
        self.assertEqual(
            blueprint.to_sql(),
            [
                "CREATE TABLE [users] "
                "([name] VARCHAR(255) NOT NULL, "
                "[age] INT NOT NULL, "
                "[profile_id] INT NOT NULL, "
                "CONSTRAINT users_name_unique UNIQUE (name), "
                "CONSTRAINT users_profile_id_foreign FOREIGN KEY ([profile_id]) REFERENCES [profiles]([id]))"
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
            blueprint.timestamp("registered_at").default_raw("CURRENT_TIMESTAMP")
            blueprint.timestamps()

        self.assertEqual(len(blueprint.table.added_columns), 10)
        self.assertEqual(
            blueprint.to_sql(),
            [
                "CREATE TABLE [users] ([id] INT IDENTITY NOT NULL, [name] VARCHAR(255) NOT NULL, [email] VARCHAR(255) NOT NULL, "
                "[password] VARCHAR(255) NOT NULL, [admin] INT NOT NULL DEFAULT 0, [remember_token] VARCHAR(255) NULL, "
                "[verified_at] DATETIME NULL, [registered_at] DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, [created_at] DATETIME NULL DEFAULT CURRENT_TIMESTAMP, "
                "[updated_at] DATETIME NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT users_id_primary PRIMARY KEY (id), CONSTRAINT users_email_unique UNIQUE (email))"
            ],
        )

    def test_can_advanced_table_creation2(self):
        with self.schema.create("users") as blueprint:
            blueprint.increments("id")
            blueprint.enum("gender", ["male", "female"])
            blueprint.string("name")
            blueprint.string("duration")
            blueprint.string("url")
            blueprint.inet("last_address").nullable()
            blueprint.cidr("route_origin").nullable()
            blueprint.macaddr("mac_address").nullable()
            blueprint.datetime("published_at")
            blueprint.string("thumbnail").nullable()
            blueprint.integer("premium")
            blueprint.integer("author_id").unsigned().nullable()
            blueprint.foreign("author_id").references("id").on("users").on_delete(
                "CASCADE"
            )
            blueprint.text("description")
            blueprint.timestamps()

        self.assertEqual(len(blueprint.table.added_columns), 15)
        self.assertEqual(
            blueprint.to_sql(),
            (
                [
                    "CREATE TABLE [users] ([id] INT IDENTITY NOT NULL, [gender] VARCHAR(255) NOT NULL CHECK([gender] IN ('male', 'female')), [name] VARCHAR(255) NOT NULL, [duration] VARCHAR(255) NOT NULL, "
                    "[url] VARCHAR(255) NOT NULL, [last_address] VARCHAR(255) NULL, [route_origin] VARCHAR(255) NULL, [mac_address] VARCHAR(255) NULL, [published_at] DATETIME NOT NULL, [thumbnail] VARCHAR(255) NULL, [premium] INT NOT NULL, "
                    "[author_id] INT NULL, [description] TEXT NOT NULL, [created_at] DATETIME NULL DEFAULT CURRENT_TIMESTAMP, "
                    "[updated_at] DATETIME NULL DEFAULT CURRENT_TIMESTAMP, "
                    "CONSTRAINT users_id_primary PRIMARY KEY (id), CONSTRAINT users_author_id_foreign FOREIGN KEY ([author_id]) REFERENCES [users]([id]) ON DELETE CASCADE)"
                ]
            ),
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
                "CREATE TABLE [users] ("
                "[profile_id] INT NOT NULL, "
                "CONSTRAINT profile_foreign FOREIGN KEY ([profile_id]) REFERENCES [profiles]([id]))"
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
                "CREATE TABLE [users] "
                "([name] VARCHAR(255) NOT NULL, "
                "[age] INT NOT NULL, "
                "[profile_id] INT NOT NULL, "
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
                "CREATE TABLE [users] "
                "([name] VARCHAR(255) NOT NULL, "
                "[age] INT NOT NULL, "
                "[profile_id] INT NOT NULL, "
                "CONSTRAINT users_name_primary PRIMARY KEY (name))"
            ],
        )

    def test_has_table(self):
        schema_sql = self.schema.has_table("users")

        sql = "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'users'"

        self.assertEqual(schema_sql, sql)

    def test_can_truncate(self):
        sql = self.schema.truncate("users")

        self.assertEqual(sql, "TRUNCATE TABLE [users]")

    def test_can_rename_table(self):
        sql = self.schema.rename("users", "clients")

        self.assertEqual(sql, "EXEC sp_rename [users], [clients]")

    def test_can_drop_table_if_exists(self):
        sql = self.schema.drop_table_if_exists("users", "clients")

        self.assertEqual(sql, "DROP TABLE IF EXISTS [users]")

    def test_can_drop_table(self):
        sql = self.schema.drop_table("users", "clients")

        self.assertEqual(sql, "DROP TABLE [users]")

    def test_has_column(self):
        sql = self.schema.has_column("users", "name")

        self.assertEqual(
            sql,
            "SELECT 1 FROM sys.columns WHERE Name = N'name' AND Object_ID = Object_ID(N'users')",
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
                "ALTER TABLE [users] NOCHECK CONSTRAINT ALL",
                "TRUNCATE TABLE [users]",
                "ALTER TABLE [users] WITH CHECK CHECK CONSTRAINT ALL",
            ],
        )
