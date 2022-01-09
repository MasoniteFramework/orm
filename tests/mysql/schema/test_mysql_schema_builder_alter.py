import unittest
import os

from tests.integrations.config.database import DATABASES
from src.masoniteorm.connections import MySQLConnection
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import MySQLPlatform
from src.masoniteorm.schema.Table import Table


class TestMySQLSchemaBuilderAlter(unittest.TestCase):
    maxDiff = None

    def setUp(self):

        self.schema = Schema(
            connection_class=MySQLConnection,
            connection="mysql",
            connection_details=DATABASES,
            platform=MySQLPlatform,
            dry=True,
        ).on("mysql")

    def test_can_add_columns(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name")
            blueprint.integer("age")

        self.assertEqual(len(blueprint.table.added_columns), 2)

        sql = [
            "ALTER TABLE `users` ADD `name` VARCHAR(255) NOT NULL, ADD `age` INT(11) NOT NULL"
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_add_column_comments(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name").comment("A users username")

        self.assertEqual(len(blueprint.table.added_columns), 1)

        sql = [
            "ALTER TABLE `users` ADD `name` VARCHAR(255) NOT NULL COMMENT 'A users username'"
        ]

    def test_can_add_table_comment(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name")
            blueprint.table_comment("A users username")

        self.assertEqual(len(blueprint.table.added_columns), 1)

        sql = [
            "ALTER TABLE `users` ADD `name` VARCHAR(255) NOT NULL COMMENT 'A users username'"
        ]

    def test_can_add_table_comment_with_no_columns(self):
        with self.schema.table("users") as blueprint:
            blueprint.table_comment("A users username")

        self.assertEqual(len(blueprint.table.added_columns), 0)

        sql = ["ALTER TABLE `users` COMMENT 'A users username'"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_add_column_after(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name").after("age")

        self.assertEqual(len(blueprint.table.added_columns), 1)

        sql = ["ALTER TABLE `users` ADD `name` VARCHAR(255) NOT NULL AFTER `age`"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_rename(self):
        with self.schema.table("users") as blueprint:
            blueprint.rename("post", "comment", "integer")

        table = Table("users")
        table.add_column("post", "integer")
        blueprint.table.from_table = table

        sql = ["ALTER TABLE `users` CHANGE `post` `comment` INT NOT NULL"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_add_and_rename(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name")
            blueprint.rename("post", "comment", "string")

        table = Table("users")
        table.add_column("post", "string")
        blueprint.table.from_table = table

        sql = [
            "ALTER TABLE `users` ADD `name` VARCHAR(255) NOT NULL",
            "ALTER TABLE `users` CHANGE `post` `comment` VARCHAR NOT NULL",
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_add_and_rename_to_string(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name")
            blueprint.rename("post", "comment", "string", length=200)

        table = Table("users")
        table.add_column("post", "integer")
        blueprint.table.from_table = table

        sql = [
            "ALTER TABLE `users` ADD `name` VARCHAR(255) NOT NULL",
            "ALTER TABLE `users` CHANGE `post` `comment` VARCHAR(200) NOT NULL",
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop1(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_column("post")

        sql = ["ALTER TABLE `users` DROP COLUMN `post`"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_add_column_and_foreign_key(self):
        with self.schema.table("users") as blueprint:
            blueprint.unsigned_integer("playlist_id").nullable()
            blueprint.foreign("playlist_id").references("id").on("playlists").on_delete(
                "cascade"
            )

        sql = [
            "ALTER TABLE `users` ADD `playlist_id` INT UNSIGNED NULL",
            "ALTER TABLE `users` ADD CONSTRAINT users_playlist_id_foreign FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE",
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop_foreign_key(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_foreign("users_playlist_id_foreign")

        sql = ["ALTER TABLE `users` DROP FOREIGN KEY users_playlist_id_foreign"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop_foreign_key_shortcut(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_foreign(["playlist_id"])

        sql = ["ALTER TABLE `users` DROP FOREIGN KEY users_playlist_id_foreign"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop_unique_constraint(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_unique("users_playlist_id_unique")

        sql = ["ALTER TABLE `users` DROP INDEX users_playlist_id_unique"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_add_index(self):
        with self.schema.table("users") as blueprint:
            blueprint.index("playlist_id")

        sql = ["CREATE INDEX users_playlist_id_index ON `users`(playlist_id)"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop_index(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_index("users_playlist_id_index")

        sql = ["ALTER TABLE `users` DROP INDEX users_playlist_id_index"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_add_primary(self):
        with self.schema.table("users") as blueprint:
            blueprint.primary("playlist_id")

        sql = [
            "ALTER TABLE `users` ADD CONSTRAINT users_playlist_id_primary PRIMARY KEY (playlist_id)"
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop_index_shortcut(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_index(["playlist_id"])

        sql = ["ALTER TABLE `users` DROP INDEX users_playlist_id_index"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop_unique_constraint_shortcut(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_unique(["playlist_id"])

        sql = ["ALTER TABLE `users` DROP INDEX users_playlist_id_unique"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_alter_drop_primary(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_primary("users_id_primary")

        sql = ["ALTER TABLE `users` DROP INDEX users_id_primary"]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_change(self):
        with self.schema.table("users") as blueprint:
            blueprint.integer("age").change()
            blueprint.string("external_type").default("external")
            blueprint.integer("gender").nullable().change()
            blueprint.string("name")

        self.assertEqual(len(blueprint.table.added_columns), 2)
        self.assertEqual(len(blueprint.table.changed_columns), 2)
        table = Table("users")
        table.add_column("age", "string")

        blueprint.table.from_table = table

        sql = [
            "ALTER TABLE `users` ADD `external_type` VARCHAR(255) NOT NULL DEFAULT 'external', ADD `name` VARCHAR(255) NOT NULL",
            "ALTER TABLE `users` MODIFY `age` INT(11) NOT NULL, MODIFY `gender` INT(11) NULL",
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_timestamp_alter_add_nullable_column(self):
        with self.schema.table("users") as blueprint:
            blueprint.timestamp("due_date").nullable()

        self.assertEqual(len(blueprint.table.added_columns), 1)

        table = Table("users")
        table.add_column("age", "string")

        blueprint.table.from_table = table

        sql = ["ALTER TABLE `users` ADD `due_date` TIMESTAMP NULL"]

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
            "ALTER TABLE `users` ADD `name` VARCHAR(255) NOT NULL",
            "ALTER TABLE `users` MODIFY `age` INT(11) NOT NULL DEFAULT 0",
            "ALTER TABLE `users` DROP COLUMN `email`",
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_create_indexes(self):
        with self.schema.table("users") as blueprint:
            blueprint.index("name")
            blueprint.index(["name", "email"])
            blueprint.unique("name")
            blueprint.unique("name", name="table_unique")
            blueprint.unique(["name", "email"])
            blueprint.fulltext("description")

        self.assertEqual(len(blueprint.table.added_columns), 0)
        print(blueprint.to_sql())
        self.assertEqual(
            blueprint.to_sql(),
            [
                "CREATE INDEX users_name_index ON `users`(name)",
                "CREATE INDEX users_name_email_index ON `users`(name,email)",
                "ALTER TABLE `users` ADD CONSTRAINT UNIQUE INDEX users_name_unique(name)",
                "ALTER TABLE `users` ADD CONSTRAINT UNIQUE INDEX table_unique(name)",
                "ALTER TABLE `users` ADD CONSTRAINT UNIQUE INDEX users_name_email_unique(name,email)",
                "ALTER TABLE `users` ADD FULLTEXT description_fulltext(description)",
            ],
        )
