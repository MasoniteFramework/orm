import os
import unittest

from tests.integrations.config.database import DATABASES
from src.masoniteorm.connections import MySQLConnection
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import MySQLPlatform


class TestMySQLSchemaBuilder(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.schema = Schema(
            connection_class=MySQLConnection,
            connection="mysql",
            connection_details=DATABASES,
            platform=MySQLPlatform,
            dry=True,
        ).on("mysql")

    def test_can_add_columns1(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.integer("age")

        self.assertEqual(len(blueprint.table.added_columns), 2)
        self.assertEqual(
            blueprint.to_sql(),
            [
                "CREATE TABLE `users` (`name` VARCHAR(255) NOT NULL, `age` INT(11) NOT NULL)"
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
                "CREATE TABLE IF NOT EXISTS `users` (`name` VARCHAR(255) NOT NULL, `age` INT(11) NOT NULL)"
            ],
        )

    def test_can_add_columns_with_constaint(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.integer("age")
            blueprint.unique("name"),
            blueprint.unique("name", name="table_unique"),

        self.assertEqual(len(blueprint.table.added_columns), 2)
        self.assertEqual(
            blueprint.to_sql(),
            [
                "CREATE TABLE `users` (`name` VARCHAR(255) NOT NULL, `age` INT(11) NOT NULL, CONSTRAINT users_name_unique UNIQUE (name), CONSTRAINT table_unique UNIQUE (name))"
            ],
        )

    def test_add_column_comment(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name").comment("A users username")

        self.assertEqual(len(blueprint.table.added_columns), 1)
        self.assertEqual(
            blueprint.to_sql(),
            [
                "CREATE TABLE `users` (`name` VARCHAR(255) NOT NULL COMMENT 'A users username')"
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
                "CREATE TABLE `users` (`name` VARCHAR(255) NOT NULL) COMMENT 'A users table'"
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
                "CREATE TABLE `users` (`name` VARCHAR(255) NOT NULL, "
                "`age` INT(11) NOT NULL, "
                "`profile_id` INT(11) NOT NULL, "
                "CONSTRAINT users_name_unique UNIQUE (name), "
                "CONSTRAINT users_profile_id_foreign FOREIGN KEY (`profile_id`) REFERENCES `profiles`(`id`))"
            ],
        )

    def test_can_add_columns_with_foreign_key_constaint(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name").unique()
            blueprint.integer("age")
            blueprint.integer("profile_id")
            blueprint.add_foreign("profile_id.id.profiles")

        self.assertEqual(len(blueprint.table.added_columns), 3)
        self.assertEqual(
            blueprint.to_sql(),
            [
                "CREATE TABLE `users` (`name` VARCHAR(255) NOT NULL, "
                "`age` INT(11) NOT NULL, "
                "`profile_id` INT(11) NOT NULL, "
                "CONSTRAINT users_name_unique UNIQUE (name), "
                "CONSTRAINT users_profile_id_foreign FOREIGN KEY (`profile_id`) REFERENCES `profiles`(`id`))"
            ],
        )

    def test_can_advanced_table_creation(self):
        with self.schema.create("users") as blueprint:
            blueprint.increments("id")
            blueprint.string("name")
            blueprint.tiny_integer("active")
            blueprint.string("email").unique()
            blueprint.enum("gender", ["male", "female"])
            blueprint.string("password")
            blueprint.decimal("money")
            blueprint.integer("admin").default(0)
            blueprint.string("option").default("ADMIN")
            blueprint.string("remember_token").nullable()
            blueprint.timestamp("verified_at").nullable()
            blueprint.timestamps()

        self.assertEqual(len(blueprint.table.added_columns), 13)
        self.assertEqual(
            blueprint.to_sql(),
            [
                "CREATE TABLE `users` (`id` INT UNSIGNED AUTO_INCREMENT NOT NULL, "
                "`name` VARCHAR(255) NOT NULL, `active` TINYINT(1) NOT NULL, `email` VARCHAR(255) NOT NULL, `gender` ENUM('male', 'female') NOT NULL, "
                "`password` VARCHAR(255) NOT NULL, `money` DECIMAL(17, 6) NOT NULL, "
                "`admin` INT(11) NOT NULL DEFAULT 0, `option` VARCHAR(255) NOT NULL DEFAULT 'ADMIN', `remember_token` VARCHAR(255) NULL, `verified_at` TIMESTAMP NULL, "
                "`created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP, `updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT users_id_primary PRIMARY KEY (id), CONSTRAINT users_email_unique UNIQUE (email))"
            ],
        )

    def test_can_add_primary_constraint_without_column_name(self):
        with self.schema.create("users") as blueprint:
            blueprint.integer("user_id").primary()
            blueprint.string("name")
            blueprint.string("email")

        self.assertEqual(len(blueprint.table.added_columns), 3)
        self.assertEqual(len(blueprint.table.added_constraints), 1)

        self.assertTrue(
            blueprint.to_sql()[0].startswith(
                "CREATE TABLE `users` (`user_id` INT(11) NOT NULL"
            )
        )

    def test_can_advanced_table_creation2(self):
        with self.schema.create("users") as blueprint:
            blueprint.big_increments("id")
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

        self.assertEqual(len(blueprint.table.added_columns), 14)
        self.assertEqual(
            blueprint.to_sql(),
            [
                "CREATE TABLE `users` (`id` BIGINT UNSIGNED AUTO_INCREMENT NOT NULL, `name` VARCHAR(255) NOT NULL, "
                "`duration` VARCHAR(255) NOT NULL, `url` VARCHAR(255) NOT NULL, `last_address` VARCHAR(255) NULL, `route_origin` VARCHAR(255) NULL, `mac_address` VARCHAR(255) NULL, "
                "`published_at` DATETIME NOT NULL, `thumbnail` VARCHAR(255) NULL, "
                "`premium` INT(11) NOT NULL, `author_id` INT UNSIGNED NULL, `description` TEXT NOT NULL, `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP, "
                "`updated_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT users_id_primary PRIMARY KEY (id), CONSTRAINT users_author_id_foreign FOREIGN KEY (`author_id`) REFERENCES `users`(`id`) ON DELETE CASCADE)"
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
                "CREATE TABLE `users` ("
                "`profile_id` INT(11) NOT NULL, "
                "CONSTRAINT profile_foreign FOREIGN KEY (`profile_id`) REFERENCES `profiles`(`id`))"
            ],
        )

    def test_can_have_composite_keys(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name").unique()
            blueprint.integer("age")
            blueprint.integer("profile_id")
            blueprint.primary(["name", "age"])

        self.assertEqual(len(blueprint.table.added_columns), 3)
        print(blueprint.to_sql())
        self.assertEqual(
            blueprint.to_sql(),
            [
                "CREATE TABLE `users` "
                "(`name` VARCHAR(255) NOT NULL, "
                "`age` INT(11) NOT NULL, "
                "`profile_id` INT(11) NOT NULL, "
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
                "CREATE TABLE `users` "
                "(`name` VARCHAR(255) NOT NULL, "
                "`age` INT(11) NOT NULL, "
                "`profile_id` INT(11) NOT NULL, "
                "CONSTRAINT users_name_primary PRIMARY KEY (name))"
            ],
        )

    def test_has_table(self):
        schema_sql = self.schema.has_table("users")

        sql = f"SELECT * from information_schema.tables where table_name='users' AND table_schema = '{os.getenv('MYSQL_DATABASE_DATABASE')}'"

        self.assertEqual(schema_sql, sql)

    def test_can_truncate(self):
        sql = self.schema.truncate("users")

        self.assertEqual(sql, "TRUNCATE `users`")

    def test_can_rename_table(self):
        sql = self.schema.rename("users", "clients")

        self.assertEqual(sql, "ALTER TABLE `users` RENAME TO `clients`")

    def test_can_drop_table_if_exists(self):
        sql = self.schema.drop_table_if_exists("users", "clients")

        self.assertEqual(sql, "DROP TABLE IF EXISTS `users`")

    def test_can_drop_table(self):
        sql = self.schema.drop_table("users", "clients")

        self.assertEqual(sql, "DROP TABLE `users`")

    def test_has_column(self):
        sql = self.schema.has_column("users", "name")

        self.assertEqual(
            sql,
            "SELECT column_name FROM information_schema.columns WHERE table_name='users' and column_name='name'",
        )

    def test_can_enable_foreign_keys(self):
        sql = self.schema.enable_foreign_key_constraints()

        self.assertEqual(sql, "SET FOREIGN_KEY_CHECKS=1")

    def test_can_disable_foreign_keys(self):
        sql = self.schema.disable_foreign_key_constraints()

        self.assertEqual(sql, "SET FOREIGN_KEY_CHECKS=0")

    def test_can_truncate_without_foreign_keys(self):
        sql = self.schema.truncate("users", foreign_keys=True)

        self.assertEqual(
            sql,
            [
                "SET FOREIGN_KEY_CHECKS=0",
                "TRUNCATE `users`",
                "SET FOREIGN_KEY_CHECKS=1",
            ],
        )
