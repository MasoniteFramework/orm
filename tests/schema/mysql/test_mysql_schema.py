from src.masonite.orm.grammar.mysql_grammar import MySQLGrammar
from src.masonite.orm.blueprint.Blueprint import Blueprint
from src.masonite.orm.grammar.GrammarFactory import GrammarFactory
from src.masonite.orm.schema.Schema import Schema
import unittest, inspect


class BaseTestCreateGrammar:
    def setUp(self):
        self.schema = Schema.on("mysql")

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

    def test_can_compile_large_blueprint(self):
        with self.schema.create("users") as blueprint:
            blueprint.string("name")
            blueprint.string("email")
            blueprint.string("password")
            blueprint.integer("age").nullable()
            blueprint.enum("type", ["Open", "Closed"])
            blueprint.datetime("pick_up")
            blueprint.binary("profile")
            blueprint.boolean("of_age")
            blueprint.char("first_initial", length=4)
            blueprint.date("birthday")
            blueprint.decimal("credit", 17, 6)
            blueprint.text("description")
            blueprint.unsigned("bank").nullable()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(blueprint.to_sql(), sql)

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


class TestMySQLCreateGrammar(BaseTestCreateGrammar, unittest.TestCase):
    def setUp(self):
        self.schema = Schema.on("mysql")

    def can_compile_column(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.string('name')
        """

        return "CREATE TABLE `users` (`name` VARCHAR(255) NOT NULL)"

    def can_compile_column_constraint(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.string('name').unique()
        """

        return "CREATE TABLE `users` (`name` VARCHAR(255) NOT NULL, CONSTRAINT name_unique UNIQUE (name))"

    def can_compile_multiple_columns(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.string('name').nullable()
            blueprint.integer('age')
        """

        return (
            "CREATE TABLE `users` ("
            "`name` VARCHAR(255), "
            "`age` INT(11) NOT NULL"
            ")"
        )

    def can_compile_not_null(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.string('name')
        """

        return "CREATE TABLE `users` (" "`name` VARCHAR(255) NOT NULL" ")"

    def can_compile_primary_key(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.increments('id')
            blueprint.string('name')
        """

        return (
            "CREATE TABLE `users` ("
            "`id` INT AUTO_INCREMENT PRIMARY KEY NOT NULL, "
            "`name` VARCHAR(255) NOT NULL"
            ")"
        )

    def can_compile_primary_key(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.increments('id')
            blueprint.string('name')
        """

        return (
            "CREATE TABLE `users` ("
            "`id` INT AUTO_INCREMENT PRIMARY KEY NOT NULL, "
            "`name` VARCHAR(255) NOT NULL"
            ")"
        )

    def can_compile_multiple_constraints(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.increments('id')
            blueprint.string('name').unique()
        """

        return (
            "CREATE TABLE `users` ("
            "`id` INT AUTO_INCREMENT PRIMARY KEY NOT NULL, "
            "`name` VARCHAR(255) NOT NULL, "
            "CONSTRAINT name_unique UNIQUE (name)"
            ")"
        )

    def can_compile_enum(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.enum('age', [1,2,3]).nullable()
        """

        return "CREATE TABLE `users` (" "`age` ENUM('1','2','3')" ")"

    def column_exists(self):
        """
        self.schema.has_column('users', 'email', query_only=True)
        """

        return "SHOW COLUMNS FROM `users` LIKE 'email'"

    def drop_table(self):
        """
        to_sql = self.schema.drop_table('users', query_only=True)
        """

        return "DROP TABLE `users`"

    def drop_table_if_exists(self):
        """
        to_sql = self.schema.drop_table_if_exists('users', query_only=True)
        """

        return "DROP TABLE IF EXISTS `users`"

    def drop_column(self):
        """
        with self.schema.table('users') as blueprint:
            blueprint.drop_column('name')
        """

        return "ALTER TABLE `users` " "DROP COLUMN `name`"

    def drop_multiple_column(self):
        """
        with self.schema.table('users') as blueprint:
            blueprint.drop_column('name', 'age', 'profile')
        """

        return (
            "ALTER TABLE `users` "
            "DROP COLUMN `name`, "
            "DROP COLUMN `age`, "
            "DROP COLUMN `profile`"
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
            "CREATE TABLE `users` ("
            "`created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
            "`updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

    def can_compile_timestamps_columns_with_default_of_now(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.timestamp('logged_at', now=True)
        """

        return "CREATE TABLE `users` (" "`logged_at` TIMESTAMP DEFAULT NOW()" ")"

    def can_compile_timestamp_column_without_default(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.timestamp('logged_at')
        """

        return "CREATE TABLE `users` (" "`logged_at` TIMESTAMP NOT NULL" ")"

    def can_compile_timestamps_columns_mixed_defaults_and_not_default(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.timestamps()
            blueprint.timestamp('logged_at')
            blueprint.timestamp('expirated_at')
        """

        return (
            "CREATE TABLE `users` ("
            "`created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
            "`updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP, "
            "`logged_at` TIMESTAMP NOT NULL, "
            "`expirated_at` TIMESTAMP NOT NULL"
            ")"
        )

    def can_compile_timestamp_nullable_columns(self):
        """
        with self.schema.create('users') as blueprint:
            blueprint.timestamp('logged_at')
            blueprint.timestamp('expirated_at').nullable()
        """

        return (
            "CREATE TABLE `users` ("
            "`logged_at` TIMESTAMP NOT NULL, "
            "`expirated_at` TIMESTAMP"
            ")"
        )
