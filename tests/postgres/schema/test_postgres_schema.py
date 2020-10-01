import inspect
import unittest

from src.masoniteorm.schema import Schema
from src.masoniteorm.connections import PostgresConnection
from src.masoniteorm.schema.grammars.PostgresGrammar import PostgresGrammar
from config.database import DATABASES


class BaseTestCreateGrammar:

    maxDiff = None

    def setUp(self):
        pass

    def test_can_compile_column(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_compile_column_constraint(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name").unique()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_compile_multiple_columns(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name").nullable()
            blueprint.integer("age")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_compile_not_null(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_compile_primary_key(self):
        with self.schema.create("users") as blueprint:
            blueprint.increments("id")
            blueprint.string("name")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_compile_multiple_constraints(self):
        with self.schema.create("users") as blueprint:
            blueprint.increments("id")
            blueprint.string("name").unique()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_compile_enum(self):
        with self.schema.create("users") as blueprint:
            blueprint.enum("age", [1, 2, 3]).nullable()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_column_exists(self):
        to_sql = self.schema.has_column("users", "email", query_only=True)

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_table_exists(self):
        to_sql = self.schema.has_table("users", query_only=True)

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_drop_table(self):
        to_sql = self.schema.drop_table("users", query_only=True)

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_drop_table_if_exists(self):
        to_sql = self.schema.drop_table_if_exists("users", query_only=True)

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_drop_column(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_column("name")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_drop_multiple_column(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_column("name", "age", "profile")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()

        self.assertEqual(blueprint.to_sql(), sql)

    # def test_can_compile_large_blueprint(self):
    #     with self.schema.create("users") as blueprint:
    #         blueprint.string("name")
    #         blueprint.string("email")
    #         blueprint.string("password")
    #         blueprint.integer("age").nullable()
    #         blueprint.enum("type", ["Open", "Closed"])
    #         blueprint.datetime("pick_up")
    #         blueprint.binary("profile")
    #         blueprint.boolean("of_age")
    #         blueprint.char("first_initial", length=4)
    #         blueprint.date("birthday")
    #         blueprint.decimal("credit", 17, 6)
    #         blueprint.text("description")
    #         blueprint.unsigned("bank").nullable()

    #     sql = getattr(
    #         self, inspect.currentframe().f_code.co_name.replace("test_", "")
    #     )()
    #     self.assertEqual(blueprint.to_sql(), sql)

    def test_can_compile_timestamps_columns_with_default(self):
        with self.schema.create("users") as blueprint:
            blueprint.timestamps()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_compile_timestamp_column_without_default(self):
        with self.schema.create("users") as blueprint:
            blueprint.timestamp("logged_at")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_compile_timestamps_columns_mixed_defaults_and_not_default(self):
        with self.schema.create("users") as blueprint:
            blueprint.timestamps()
            blueprint.timestamp("logged_at")
            blueprint.timestamp("expirated_at")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_compile_timestamp_nullable_columns(self):
        with self.schema.create("users") as blueprint:
            blueprint.timestamp("logged_at")
            blueprint.timestamp("expirated_at").nullable()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_can_compile_timestamps_columns_with_default_of_now(self):
        with self.schema.create("users") as blueprint:
            blueprint.timestamp("logged_at", now=True)

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_rename_table(self):
        to_sql = self.schema.rename("users", "core", query_only=True)

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_unique_constraint(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.unique("email")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_fulltext_constraint(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.fulltext("description")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_primary_constraint(self):
        with self.schema.create("users") as blueprint:
            blueprint.integer("id")
            blueprint.string("name")
            blueprint.primary("id")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_index_constraint(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.index("email")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
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

    def test_multiple_index_constraint(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.index(["email", "name"])

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_truncate_table(self):
        to_sql = self.schema.truncate("users", query_only=True)

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_rename_column(self):
        with self.schema.table("users") as blueprint:
            blueprint.rename("name", "first_name")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_drop_index(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_index("name_index")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_drop_multiple_index(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_index(["name_index", "email_index"])

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_drop_unique(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_unique("name_unique")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_drop_multiple_unique(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_unique(["name_unique", "email_unique"])

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_drop_primary(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_primary()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_drop_foreign(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_foreign("users_article_id_foreign")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

    def test_drop_multiple_foreign(self):
        with self.schema.table("users") as blueprint:
            blueprint.drop_foreign(["article_id", "post_id"])

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)


class TestPostgresCreateGrammar(BaseTestCreateGrammar, unittest.TestCase):
    def setUp(self):
        self.schema = Schema(
            connection=PostgresConnection,
            grammar=PostgresGrammar,
            dry=True,
            connection_driver="postgres",
        )

    def can_compile_column(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.string('name')
        """

        return """CREATE TABLE "users" ("name" VARCHAR(255) NOT NULL)"""

    def can_compile_column_constraint(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.string('name').unique()
        """
        return """CREATE TABLE "users" ("name" VARCHAR(255) NOT NULL, CONSTRAINT name_unique UNIQUE (name))"""

    def can_compile_multiple_columns(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.string('name').nullable()
            blueprint.integer('age')
        """

        return (
            """CREATE TABLE "users" ("""
            """\"name" VARCHAR(255) NULL, """
            """\"age" INTEGER NOT NULL"""
            """)"""
        )

    def can_compile_not_null(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.string('name')
        """

        return """CREATE TABLE "users" (""" """\"name" VARCHAR(255) NOT NULL""" """)"""

    def can_compile_primary_key(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.increments('id')
            blueprint.string('name')
        """

        return (
            """CREATE TABLE "users" ("""
            """\"id" SERIAL UNIQUE NOT NULL, """
            """\"name" VARCHAR(255) NOT NULL"""
            """)"""
        )

    def can_compile_multiple_constraints(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.increments('id')
            blueprint.string('name').unique()
        """

        return (
            """CREATE TABLE "users" ("""
            """\"id" SERIAL UNIQUE NOT NULL, """
            """\"name" VARCHAR(255) NOT NULL, """
            """CONSTRAINT name_unique UNIQUE (name)"""
            """)"""
        )

    def can_compile_enum(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.enum('age', [1,2,3]).nullable()
        """

        return (
            """CREATE TABLE "users" ("""
            """\"age" VARCHAR(255) CHECK ("age" in ('1','2','3'))"""
            """)"""
        )

    def unique_constraint(self):
        """
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.unique('email')
        """

        return (
            """CREATE TABLE "users" ("""
            """\"name" VARCHAR(255) NOT NULL, """
            """CONSTRAINT email_unique UNIQUE (email)"""
            """)"""
        )

    def index_constraint(self):
        """
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.index("email")
        """

        return (
            """CREATE TABLE "users" ("""
            """\"name" VARCHAR(255) NOT NULL"""
            """); CREATE INDEX users_email_index ON "users"("email")"""
        )

    def fulltext_constraint(self):
        """
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.fulltext('description')
        """
        return (
            """CREATE TABLE "users" ("""
            """\"name" VARCHAR(255) NOT NULL"""
            """); CREATE INDEX users_description_index ON "users"("description")"""
        )

    def primary_constraint(self):
        """
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.primary('id')
        """

        return (
            """CREATE TABLE "users" ("""
            """\"id" INTEGER NOT NULL, """
            """\"name" VARCHAR(255) NOT NULL, """
            """PRIMARY KEY ("id")"""
            """)"""
        )

    def multiple_index_constraint(self):
        """
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.index(["email", "name"])
        """

        return (
            """CREATE TABLE "users" ("""
            """\"name" VARCHAR(255) NOT NULL"""
            """); CREATE INDEX users_email_index ON "users"("email"); """
            """CREATE INDEX users_name_index ON "users"("name")"""
        )

    def foreign_key_constraint(self):
        """
        with self.schema.create("users") as blueprint:
            blueprint.integer("user_id").unsigned()
            blueprint.foreign('user_id').references('id').on('profile')
            blueprint.foreign('fruit_id').references('id').on('fruit')
        """

        return (
            """CREATE TABLE "users" ("""
            """\"user_id" INT NOT NULL, """
            """CONSTRAINT users_user_id_foreign FOREIGN KEY ("user_id") REFERENCES "profile"("id"), """
            """CONSTRAINT users_fruit_id_foreign FOREIGN KEY ("fruit_id") REFERENCES "fruit"("id")"""
            """)"""
        )

    def column_exists(self):
        """
        self.schema.has_column('users', 'email', query_only=True)
        """

        return (
            """SELECT column_name """
            """FROM information_schema.columns """
            """WHERE table_name='users' and column_name='email'"""
        )

    def table_exists(self):
        """
        self.schema.has_table('users', query_only=True)
        """
        return "SELECT * from information_schema.tables where table_name='users'"

    def drop_table(self):
        """
        to_sql = self.schema.drop_table('users', query_only=True)
        """

        return """DROP TABLE "users\""""

    def drop_table_if_exists(self):
        """
        to_sql = self.schema.drop_table_if_exists('users', query_only=True)
        """

        return """DROP TABLE IF EXISTS "users\""""

    def drop_column(self):
        """
        with self.schema.table('users') as blueprint:
            blueprint.drop_column('name')
        """

        return """ALTER TABLE "users\" """ """DROP COLUMN "name\""""

    def drop_multiple_column(self):
        """
        with self.schema.table('users') as blueprint:
            blueprint.drop_column('name', 'age', 'profile')
        """

        return (
            """ALTER TABLE "users" """
            """DROP COLUMN "name", """
            """DROP COLUMN "age", """
            """DROP COLUMN "profile\""""
        )

    def can_compile_large_blueprint(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.string('name')
            blueprint.string('email')
            blueprint.string('password')
            blueprint.integer('age').nullable()
            blueprint.enum('type', ['Open', 'Closed'])
            blueprint.datetime('pick_up')
            blueprint.binary('profile')
            blueprint.boolean('of_age')
            blueprint.char('first_initial', length=4)
            blueprint.date('birthday')
            blueprint.decimal('credit', 17,6)
            blueprint.text('description')
            blueprint.unsigned('bank').nullable()
        """

        return (
            "CREATE TABLE `users` ("
            "`name` VARCHAR(255) NOT NULL, "
            "`email` VARCHAR(255) NOT NULL, "
            "`password` VARCHAR(255) NOT NULL, "
            "`age` INT(11), "
            "`type` ENUM('Open','Closed') NOT NULL, "
            "`pick_up` DATETIME NOT NULL, "
            "`profile` LONGBLOB NOT NULL, "
            "`of_age` BOOLEAN NOT NULL, "
            "`first_initial` CHAR(4) NOT NULL, "
            "`birthday` DATE NOT NULL, "
            "`credit` DECIMAL(17, 6) NOT NULL, "
            "`description` TEXT NOT NULL, "
            "`bank` INT UNSIGNED"
            ")"
        )

    def test_default_string_length(self):
        with self.schema.table("users") as blueprint:
            blueprint.string("name")

        self.assertEqual(str(blueprint._columns[0].length), "255")

        return "ALTER TABLE `users` " "ADD `name` VARCHAR(255) NOT NULL"

        self.assertEqual(blueprint.to_sql(), sql)

        Schema.set_default_string_length("191")

        with self.schema.table("users") as blueprint:
            blueprint.string("name")

        self.assertEqual(str(blueprint._columns[0].length), "191")

        return "ALTER TABLE `users` " "ADD `name` VARCHAR(191) NOT NULL"

        self.assertEqual(blueprint.to_sql(), sql)

    def can_compile_timestamps_columns_with_default(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.timestamps()
        """

        return (
            """CREATE TABLE "users" ("""
            """\"created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, """
            """\"updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"""
            """)"""
        )

    def can_compile_timestamps_columns_with_default_of_now(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.timestamp('logged_at', now=True)
        """

        return (
            """CREATE TABLE "users" ("""
            """\"logged_at" TIMESTAMP NOT NULL DEFAULT NOW()"""
            """)"""
        )

    def can_compile_timestamp_column_without_default(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.timestamp('logged_at')
        """

        return (
            """CREATE TABLE "users" ("""
            """\"logged_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"""
            """)"""
        )

    def can_compile_timestamps_columns_mixed_defaults_and_not_default(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.timestamps()
            blueprint.timestamp('logged_at')
            blueprint.timestamp('expirated_at')
        """

        return (
            """CREATE TABLE "users" ("""
            """\"created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, """
            """\"updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, """
            """\"logged_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, """
            """\"expirated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"""
            """)"""
        )

    def can_compile_timestamp_nullable_columns(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.timestamp('logged_at')
            blueprint.timestamp('expirated_at').nullable()
        """

        return (
            """CREATE TABLE "users" ("""
            """\"logged_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, """
            """\"expirated_at" TIMESTAMP NULL DEFAULT NULL"""
            """)"""
        )

    def rename_table(self):
        """
        to_sql = self.schema.rename("users", "core", query_only=True)
        """

        return """ALTER TABLE "users" RENAME TO "core\""""

    def truncate_table(self):
        """
        to_sql = self.schema.truncate("users", query_only=True)
        """

        return """TRUNCATE "users\""""

    def drop_index(self):
        """
        with self.schema.table("users") as blueprint:
           blueprint.drop_index('name_index')
        """
        return """DROP INDEX "name_index\";"""

    def drop_multiple_index(self):
        """
        with self.schema.table("users") as blueprint:
           blueprint.drop_index(['name_index', 'email_index'])
        """
        return """DROP INDEX "name_index"; """ """DROP INDEX "email_index";"""

    def drop_unique(self):
        """
        with self.schema.table("users") as blueprint:
           blueprint.drop_unique('name_unique')
        """
        return """ALTER TABLE "users" DROP CONSTRAINT name_unique"""

    def drop_multiple_unique(self):
        """
        with self.schema.table("users") as blueprint:
           blueprint.drop_unique(['name_unique', 'email_unique'])
        """
        return """ALTER TABLE "users" DROP CONSTRAINT name_unique, DROP CONSTRAINT email_unique"""

    def drop_primary(self):
        """
        with self.schema.table("users") as blueprint:
           blueprint.drop_primary()
        """
        return """ALTER TABLE "users" DROP CONSTRAINT users_primary"""

    def drop_foreign(self):
        """
        with self.schema.table("users") as blueprint:
           blueprint.drop_foreign('users_article_id_foreign')
        """
        return """ALTER TABLE "users" """ """DROP CONSTRAINT users_article_id_foreign"""

    def drop_multiple_foreign(self):
        """
        with self.schema.table("users") as blueprint:
           blueprint.drop_foreign(('article_id', 'post_id'))
        """
        return (
            """ALTER TABLE "users" """
            """DROP CONSTRAINT users_article_id_foreign, """
            """DROP CONSTRAINT users_post_id_foreign"""
        )

    def rename_column(self):
        """
        with self.schema.table("users") as blueprint:
            blueprint.rename("name", "first_name")
        """
        return """ALTER TABLE "users" RENAME COLUMN "name" TO "first_name\""""
