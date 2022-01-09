import unittest

from tests.integrations.config.database import DATABASES
from src.masoniteorm.connections import MSSQLConnection
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import MSSQLPlatform
from src.masoniteorm.schema.Table import Table


class TestMySQLSchemaBuilderAlter(unittest.TestCase):
    maxDiff = None

    def setUp(self):

        self.schema = Schema(
            connection_class=MSSQLConnection,
            connection="mssql",
            connection_details=DATABASES,
            platform=MSSQLPlatform,
            dry=True,
        )

    def test_can_add_columns(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name")
            blueprint.integer("age")

        self.assertEqual(len(blueprint.table.added_columns), 2)

        sql = [
            "ALTER TABLE [users] ADD [name] VARCHAR(255) NOT NULL, [age] INT NOT NULL"
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_adds_column_with_default(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name").default(0)

        self.assertEqual(len(blueprint.table.added_columns), 1)

        sql = ["ALTER TABLE [users] ADD [name] VARCHAR(255) NOT NULL DEFAULT 0"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_rename(self):
        with self.schema.table("users") as blueprint:
            blueprint.rename("post", "comment", "integer")

        table = Table("users")
        table.add_column("post", "integer")
        blueprint.table.from_table = table

        sql = ["EXEC sp_rename 'users.post', 'comment', 'COLUMN'"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_add_and_rename(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name")
            blueprint.rename("post", "comment", "integer")

        table = Table("users")
        table.add_column("post", "integer")
        blueprint.table.from_table = table

        sql = [
            "ALTER TABLE [users] ADD [name] VARCHAR(255) NOT NULL",
            "EXEC sp_rename 'users.post', 'comment', 'COLUMN'",
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop1(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_column("post")

        sql = ["ALTER TABLE [users] DROP COLUMN post"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_add_column_and_foreign_key(self):
        with self.schema.table("users") as blueprint:
            blueprint.unsigned_integer("playlist_id").nullable()
            blueprint.foreign("playlist_id").references("id").on("playlists").on_delete(
                "cascade"
            )

        sql = [
            "ALTER TABLE [users] ADD [playlist_id] INT NULL",
            "ALTER TABLE [users] ADD CONSTRAINT users_playlist_id_foreign FOREIGN KEY ([playlist_id]) REFERENCES [playlists]([id]) ON DELETE CASCADE",
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_add_column_and_add_foreign(self):
        with self.schema.table("users") as blueprint:
            blueprint.unsigned_integer("playlist_id").nullable()
            blueprint.add_foreign("playlist_id.id.playlists").on_delete("cascade")

        sql = [
            "ALTER TABLE [users] ADD [playlist_id] INT NULL",
            "ALTER TABLE [users] ADD CONSTRAINT users_playlist_id_foreign FOREIGN KEY ([playlist_id]) REFERENCES [playlists]([id]) ON DELETE CASCADE",
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop_foreign_key(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_foreign("users_playlist_id_foreign")

        sql = ["ALTER TABLE [users] DROP CONSTRAINT users_playlist_id_foreign"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop_foreign_key_shortcut(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_foreign(["playlist_id"])

        sql = ["ALTER TABLE [users] DROP CONSTRAINT users_playlist_id_foreign"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop_unique_constraint(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_unique("users_playlist_id_unique")

        sql = ["DROP INDEX [users].[users_playlist_id_unique]"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_add_primary(self):
        with self.schema.table("users") as blueprint:
            blueprint.primary("playlist_id")

        sql = [
            "ALTER TABLE [users] ADD CONSTRAINT users_playlist_id_primary PRIMARY KEY (playlist_id)"
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_add_index(self):
        with self.schema.table("users") as blueprint:
            blueprint.index("playlist_id")

        sql = ["CREATE INDEX users_playlist_id_index ON [users](playlist_id)"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop_index(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_index("users_playlist_id_index")

        sql = ["DROP INDEX [users].[users_playlist_id_index]"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop_index_shortcut(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_index(["playlist_id"])

        sql = ["DROP INDEX [users].[users_playlist_id_index]"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop_unique_constraint_shortcut(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_unique(["playlist_id"])

        sql = ["DROP INDEX [users].[users_playlist_id_unique]"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop_primary(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_primary(["id"])

        sql = ["DROP INDEX [users].[users_id_primary]"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_has_table(self):
        schema_sql = self.schema.has_table("users")

        sql = "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'users'"

        self.assertEqual(schema_sql, sql)

    def test_drop_table(self):
        schema_sql = self.schema.has_table("users")

        sql = "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'users'"

        self.assertEqual(schema_sql, sql)

    def test_change(self):
        with self.schema.table("users") as blueprint:
            blueprint.integer("age").change()
            blueprint.string("name")
            blueprint.string("external_type").default("external")

        self.assertEqual(len(blueprint.table.added_columns), 2)
        self.assertEqual(len(blueprint.table.changed_columns), 1)
        table = Table("users")
        table.add_column("age", "string")

        blueprint.table.from_table = table

        sql = [
            "ALTER TABLE [users] ADD [name] VARCHAR(255) NOT NULL, [external_type] VARCHAR(255) NOT NULL DEFAULT 'external'",
            "ALTER TABLE [users] ALTER COLUMN [age] INT NOT NULL",
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_drop_add_and_change(self):
        with self.schema.table("users") as blueprint:
            blueprint.integer("age").default(0).change()
            blueprint.string("name")
            blueprint.drop_column("email")

        self.assertEqual(len(blueprint.table.added_columns), 1)
        self.assertEqual(len(blueprint.table.changed_columns), 1)
        table = Table("users")
        table.add_column("age", "string")
        table.add_column("email", "string")

        blueprint.table.from_table = table

        sql = [
            "ALTER TABLE [users] ADD [name] VARCHAR(255) NOT NULL",
            "ALTER TABLE [users] ALTER COLUMN [age] INT NOT NULL DEFAULT 0",
            "ALTER TABLE [users] DROP COLUMN email",
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_create_indexes(self):
        with self.schema.table("users") as blueprint:
            blueprint.index("name")
            blueprint.index(["name", "email"])
            blueprint.unique("name")
            blueprint.unique(["name", "email"])
            blueprint.fulltext("description")

        self.assertEqual(len(blueprint.table.added_columns), 0)
        print(blueprint.to_sql())
        self.assertEqual(
            blueprint.to_sql(),
            [
                "CREATE INDEX users_name_index ON [users](name)",
                "CREATE INDEX users_name_email_index ON [users](name,email)",
                "ALTER TABLE [users] ADD CONSTRAINT users_name_unique UNIQUE(name)",
                "ALTER TABLE [users] ADD CONSTRAINT users_name_email_unique UNIQUE(name,email)",
            ],
        )

    def test_timestamp_alter_add_nullable_column(self):
        with self.schema.table("users") as blueprint:
            blueprint.timestamp("due_date").nullable()

        self.assertEqual(len(blueprint.table.added_columns), 1)

        table = Table("users")
        table.add_column("age", "string")

        blueprint.table.from_table = table

        sql = ["ALTER TABLE [users] ADD [due_date] DATETIME NULL"]

        self.assertEqual(blueprint.to_sql(), sql)
