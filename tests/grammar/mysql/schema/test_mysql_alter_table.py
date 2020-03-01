from src.masonite.orm.grammar.mysql_grammar import MySQLGrammar
from src.masonite.orm.blueprint.Blueprint import Blueprint
from src.masonite.orm.grammar.GrammarFactory import GrammarFactory
from src.masonite.orm.schema.Schema import Schema
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
