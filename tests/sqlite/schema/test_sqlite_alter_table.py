from src.masoniteorm.schema.Blueprint import Blueprint, Column
from src.masoniteorm.schema.grammars import GrammarFactory
from src.masoniteorm.connections import SQLiteConnection
from src.masoniteorm.schema.grammars import SQLiteGrammar
from config.database import DATABASES
from src.masoniteorm.schema import Schema
import unittest

class MockSQLiteGrammarForDroppingColumn(SQLiteGrammar):

    def get_table_columns(self):
        columns = (Column("integer", "age", nullable=False), Column("string", "name", nullable=False), Column("string", "email", nullable=False))
        return columns

class TestSqliteAlterGrammar(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.schema = Schema(
            connection=SQLiteConnection,
            grammar=SQLiteGrammar,
            connection_details=DATABASES,
            connection_driver="sqlite",
            dry=True,
        )

    def test_can_compile_add_column(self):
        schema = Schema(
            connection=SQLiteConnection,
            grammar=MockSQLiteGrammarForDroppingColumn,
            connection_details=DATABASES,
            connection_driver="sqlite",
            dry=True
        )

        with schema.table("users") as blueprint:
            blueprint.string("active")

        sql = [
            'CREATE TEMPORARY TABLE __temp__users as select age, name, email from "users"',
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("age" INTEGER NOT NULL, "name" VARCHAR NOT NULL, "email" VARCHAR NOT NULL, "active" VARCHAR(255) NOT NULL)',
            'INSERT INTO "users" (age, name, email) select age, name, email from __temp__users',
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_add_multiple(self):
        schema = Schema(
            connection=SQLiteConnection,
            grammar=MockSQLiteGrammarForDroppingColumn,
            connection_details=DATABASES,
            connection_driver="sqlite",
            dry=True
        )

        with schema.table("users") as blueprint:
            blueprint.string("col1")
            blueprint.string("col2").nullable()

        sql = [
            'CREATE TEMPORARY TABLE __temp__users as select age, name, email from "users"',
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("age" INTEGER NOT NULL, "name" VARCHAR NOT NULL, "email" VARCHAR NOT NULL, "col1" VARCHAR(255) NOT NULL, "col2" VARCHAR(255) NULL)',
            'INSERT INTO "users" (age, name, email) select age, name, email from __temp__users',
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_add_with_after_column(self):
        schema = Schema(
            connection=SQLiteConnection,
            grammar=MockSQLiteGrammarForDroppingColumn,
            connection_details=DATABASES,
            connection_driver="sqlite",
            dry=True
        )

        with schema.table("users") as blueprint:
            blueprint.string("col1")
            blueprint.string("col2").nullable()
        
        sql = [
            'CREATE TEMPORARY TABLE __temp__users as select age, name, email from "users"',
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("age" INTEGER NOT NULL, "name" VARCHAR NOT NULL, "email" VARCHAR NOT NULL, "col1" VARCHAR(255) NOT NULL, "col2" VARCHAR(255) NULL)',
            'INSERT INTO "users" (age, name, email) select age, name, email from __temp__users',
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_drop_column(self):
        schema = Schema(
            connection=SQLiteConnection,
            grammar=MockSQLiteGrammarForDroppingColumn,
            connection_details=DATABASES,
            connection_driver="sqlite",
            dry=True
        )

        with schema.table("modify") as blueprint:
            blueprint.drop_column("email")

        sql = [
            'CREATE TEMPORARY TABLE __temp__modify as select age, name from "modify"',
            'DROP TABLE "modify"',
            'CREATE TABLE "modify" ("age" INTEGER NOT NULL, "name" VARCHAR NOT NULL)',
            'INSERT INTO "modify" (age, name) select age, name from __temp__modify',
        ]

        print('bb', blueprint.to_sql())

        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_change_column(self):
        schema = Schema(
            connection=SQLiteConnection,
            grammar=MockSQLiteGrammarForDroppingColumn,
            connection_details=DATABASES,
            connection_driver="sqlite",
            dry=True
        )

        with schema.table("users") as blueprint:
            blueprint.string("name", 50).nullable().change()

        sql = [
            'CREATE TEMPORARY TABLE __temp__users as select age, name, email from "users"',
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("age" INTEGER NOT NULL, "name" VARCHAR(50) NULL, "email" VARCHAR NOT NULL)',
            'INSERT INTO "users" (age, name, email) select age, name, email from __temp__users',
        ]

        print(blueprint.to_sql())
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_index(self):
        schema = Schema(
            connection=SQLiteConnection,
            grammar=MockSQLiteGrammarForDroppingColumn,
            connection_details=DATABASES,
            connection_driver="sqlite",
            dry=True
        )

        with schema.table("users") as blueprint:
            blueprint.unique("name")

        sql = [
            'CREATE TEMPORARY TABLE __temp__users as select age, name, email from "users"',
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("age" INTEGER NOT NULL, "name" VARCHAR NOT NULL, "email" VARCHAR NOT NULL, CONSTRAINT name_unique UNIQUE(name))',
            'INSERT INTO "users" (age, name, email) select age, name, email from __temp__users',
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_foreign_key(self):
        schema = Schema(
            connection=SQLiteConnection,
            grammar=MockSQLiteGrammarForDroppingColumn,
            connection_details=DATABASES,
            connection_driver="sqlite",
            dry=True
        )

        with schema.table("users") as blueprint:
            blueprint.foreign("profile_id").references("id").on("profile")

        sql = [
            'CREATE TEMPORARY TABLE __temp__users as select age, name, email from "users"',
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("age" INTEGER NOT NULL, "name" VARCHAR NOT NULL, "email" VARCHAR NOT NULL, CONSTRAINT users_profile_id_foreign FOREIGN KEY ("profile_id") REFERENCES "profile"("id"))',
            'INSERT INTO "users" (age, name, email) select age, name, email from __temp__users',
        ]

        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_foreign_key_with_on_delete(self):
        schema = Schema(
            connection=SQLiteConnection,
            grammar=MockSQLiteGrammarForDroppingColumn,
            connection_details=DATABASES,
            connection_driver="sqlite",
            dry=True
        )

        with schema.table("users") as blueprint:
            blueprint.foreign("profile_id").references("id").on("profile").on_delete(
                "cascade"
            )

        sql = [
            'CREATE TEMPORARY TABLE __temp__users as select age, name, email from "users"',
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("age" INTEGER NOT NULL, "name" VARCHAR NOT NULL, "email" VARCHAR NOT NULL, CONSTRAINT users_profile_id_foreign FOREIGN KEY ("profile_id") REFERENCES "profile"("id") ON DELETE CASCADE)',
            'INSERT INTO "users" (age, name, email) select age, name, email from __temp__users',
        ]
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_foreign_key_with_on_update(self):
        schema = Schema(
            connection=SQLiteConnection,
            grammar=MockSQLiteGrammarForDroppingColumn,
            connection_details=DATABASES,
            connection_driver="sqlite",
            dry=True
        )

        with schema.table("users") as blueprint:
            blueprint.foreign("profile_id").references("id").on("profile").on_update(
                "cascade"
            )

        sql = [
            'CREATE TEMPORARY TABLE __temp__users as select age, name, email from "users"',
            'DROP TABLE "users"',
            'CREATE TABLE "users" ("age" INTEGER NOT NULL, "name" VARCHAR NOT NULL, "email" VARCHAR NOT NULL, CONSTRAINT users_profile_id_foreign FOREIGN KEY ("profile_id") REFERENCES "profile"("id") ON UPDATE CASCADE)',
            'INSERT INTO "users" (age, name, email) select age, name, email from __temp__users',
        ]

        self.assertEqual(blueprint.to_sql(), sql)
