from src.masonite.orm.grammar.mysql_grammar import MySQLGrammar
from src.masonite.orm.blueprint import Blueprint
from src.masonite.orm.grammar import GrammarFactory
from src.masonite.orm.schema import Schema
import unittest


class TestMySQLAlterGrammar(unittest.TestCase):
    def setUp(self):
        self.schema = Schema.on("mysql")
        print(self.schema)

    def test_can_compile_alter_column(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name")

        sql = "ALTER TABLE `users` ADD `name` VARCHAR(255) NOT NULL"
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_multiple(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name")
            blueprint.string("age").nullable()

        sql = "ALTER TABLE `users` ADD `name` VARCHAR(255) NOT NULL, ADD `age` VARCHAR(255)"
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_after_column(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name")
            blueprint.string("age").nullable().after("name")

        sql = "ALTER TABLE `users` ADD `name` VARCHAR(255) NOT NULL, ADD `age` VARCHAR(255) AFTER `name`"
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_drop_column(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_column("name")

        sql = "ALTER TABLE `users` DROP COLUMN `name`"
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_change_column(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name", 50).nullable().change()

        sql = "ALTER TABLE `users` MODIFY `name` VARCHAR(50) NULL"
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_index(self):
        with self.schema.table("users") as blueprint:
            blueprint.unique("name")

        sql = "ALTER TABLE `users` ADD CONSTRAINT name_unique UNIQUE(`name`)"
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_foreign_key(self):
        with self.schema.table("users") as blueprint:
            blueprint.foreign("profile_id").references("id").on("profile")

        sql = "ALTER TABLE `users` ADD CONSTRAINT users_profile_id_foreign FOREIGN KEY (`profile_id`) REFERENCES `profile`(`id`)"
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_foreign_key_with_on_delete(self):
        with self.schema.table("users") as blueprint:
            blueprint.foreign("profile_id").references("id").on("profile").on_delete(
                "cascade"
            )

        sql = "ALTER TABLE `users` ADD CONSTRAINT users_profile_id_foreign FOREIGN KEY (`profile_id`) REFERENCES `profile`(`id`) ON DELETE CASCADE"
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_foreign_key_with_on_update(self):
        with self.schema.table("users") as blueprint:
            blueprint.foreign("profile_id").references("id").on("profile").on_update(
                "cascade"
            )

        sql = "ALTER TABLE `users` ADD CONSTRAINT users_profile_id_foreign FOREIGN KEY (`profile_id`) REFERENCES `profile`(`id`) ON UPDATE CASCADE"
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_modify_column(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_column("name")

        sql = "ALTER TABLE `users` DROP COLUMN `name`"
        self.assertEqual(blueprint.to_sql(), sql)
