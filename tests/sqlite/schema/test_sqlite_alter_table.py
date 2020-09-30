from src.masoniteorm.schema.Blueprint import Blueprint
from src.masoniteorm.schema.grammars import GrammarFactory
from src.masoniteorm.connections import SQLiteConnection
from src.masoniteorm.schema.grammars import SQLiteGrammar
from config.database import DATABASES
from src.masoniteorm.schema import Schema
import unittest
import inspect


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

    def test_can_compile_alter_column(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name")

        sql = """ALTER TABLE "users" ADD "name" VARCHAR(255) NOT NULL"""
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_multiple(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name")
            blueprint.string("age").nullable()

        sql = """ALTER TABLE "users" ADD "name" VARCHAR(255) NOT NULL, ADD "age" VARCHAR(255)"""
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_after_column(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name")
            blueprint.string("age").nullable().after("name")

        sql = """ALTER TABLE "users" ADD "name" VARCHAR(255) NOT NULL, ADD "age" VARCHAR(255) AFTER "name\""""
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_drop_column(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_column("name")

        sql = """ALTER TABLE "users" DROP COLUMN "name\""""
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_change_column(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name", 50).nullable().change()

        sql = """ALTER TABLE "users" MODIFY "name" VARCHAR(50) NULL"""
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_index(self):
        with self.schema.table("users") as blueprint:
            blueprint.unique("name")

        sql = """ALTER TABLE "users" ADD CONSTRAINT name_unique UNIQUE("name")"""
        self.assertEqual(blueprint.to_sql(), sql)
    
    def test_foreign_key_constraint(self):
        with self.schema.create("users") as blueprint:
            blueprint.unsigned("user_id")
            blueprint.foreign("user_id").references("id").on("profile")
            blueprint.foreign("fruit_id").references("id").on("fruit")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)
    
    def test_a_second_foreign_key_constraint(self):
        with self.schema.table('videos') as blueprint:
            blueprint.unsigned_integer('playlist_id').nullable()
            blueprint.foreign('playlist_id').references('id').on('playlists')

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_foreign_key(self):
        with self.schema.table("users") as blueprint:
            blueprint.unsigned_integer('profile_id').nullable()
            blueprint.foreign("profile_id").references("id").on("profile")

        sql = """ALTER TABLE "users" ADD "profile_id" INTEGER, CONSTRAINT users_profile_id_foreign REFERENCES "profile"("id")"""
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_foreign_key_with_on_delete(self):
        with self.schema.table("users") as blueprint:
            blueprint.unsigned_integer('profile_id').nullable()
            blueprint.foreign("profile_id").references("id").on("profile").on_delete(
                "cascade"
            )

        sql = """ALTER TABLE "users" ADD "profile_id" INTEGER, CONSTRAINT users_profile_id_foreign REFERENCES "profile"("id") ON DELETE CASCADE"""
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_foreign_key_with_on_update(self):
        with self.schema.table("users") as blueprint:
            blueprint.unsigned_integer('profile_id').nullable()
            blueprint.foreign("profile_id").references("id").on("profile").on_update(
                "cascade"
            )

        sql = """ALTER TABLE "users" ADD "profile_id" INTEGER, CONSTRAINT users_profile_id_foreign REFERENCES "profile"("id") ON UPDATE CASCADE"""
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_alter_modify_column(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_column("name")

        sql = """ALTER TABLE "users" DROP COLUMN "name\""""
        self.assertEqual(blueprint.to_sql(), sql)

    def foreign_key_constraint(self):
        """
        with self.schema.create("users") as blueprint:
            blueprint.integer("user_id").unsigned()
            blueprint.foreign('user_id').references('id').on('profile')
            blueprint.foreign('fruit_id').references('id').on('fruit')
        """

        return (
            """CREATE TABLE "users" ("""
            """\"user_id" INTEGER NOT NULL, """
            """ADD CONSTRAINT users_user_id_foreign FOREIGN KEY ("user_id") REFERENCES "profile"("id"), """
            """ADD CONSTRAINT users_fruit_id_foreign FOREIGN KEY ("fruit_id") REFERENCES "fruit"("id")"""
            """)"""
        )
    
    def a_second_foreign_key_constraint(self):
        """
        with self.schema.table('videos') as table:
            table.unsigned_integer('playlist_id').nullable()
            table.foreign('playlist_id').references('id').on('playlists')
        """

        return (
            """ALTER TABLE "videos" """
            """ADD "playlist_id" INTEGER, """
            """CONSTRAINT videos_playlist_id_foreign """
            """REFERENCES "playlists"("id")"""
        )