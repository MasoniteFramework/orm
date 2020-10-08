import unittest
from src.masoniteorm.schema import Table
from src.masoniteorm.schema import Column
from src.masoniteorm.schema.platforms.SQLitePlatform import SQLitePlatform
from src.masoniteorm.schema.TableDiff import TableDiff

class TestTableDiff(unittest.TestCase):

    def setUp(self):
        self.platform = SQLitePlatform()

    def test_rename_table(self):
        table = Table("users")
        table.add_column("name", "string")

        diff = TableDiff("users")
        diff.from_table = table
        diff.new_name = "clients"

        sql = ["ALTER TABLE users RENAME TO clients"]

        self.assertEqual(sql, self.platform.compile_alter_sql(diff))

    def test_drop_index(self):
        table = Table("users")
        table.add_index("name", "unique")
        

        diff = TableDiff("users")
        diff.from_table = table
        diff.remove_index("name")

        sql = ["DROP INDEX name"]

        self.assertEqual(sql, self.platform.compile_alter_sql(diff))

    def test_drop_index_and_rename_table(self):
        table = Table("users")
        table.add_index("name", "unique")
        

        diff = TableDiff("users")
        diff.from_table = table
        diff.new_name = "clients"
        diff.remove_index("name")

        sql = ["DROP INDEX name", "ALTER TABLE users RENAME TO clients"]

        self.assertEqual(sql, self.platform.compile_alter_sql(diff))

    def test_alter_add_column(self):
        table = Table("users")
        
        diff = TableDiff("users")
        diff.from_table = table
        diff.add_column("name", 'string')
        diff.add_column("email", 'string')

        sql = ["ALTER TABLE users ADD COLUMN name VARCHAR", "ALTER TABLE users ADD COLUMN email VARCHAR"]

        self.assertEqual(sql, self.platform.compile_alter_sql(diff))

    def test_alter_rename(self):
        table = Table("users")
        table.add_column("post", "integer")
        
        diff = TableDiff("users")
        diff.from_table = table
        diff.rename_column("post", "comment", "integer")

        sql = [
            "CREATE TEMPORARY TABLE __temp__users AS SELECT post FROM users", 
            "DROP TABLE users",
            'CREATE TABLE "users" (comment INTEGER)',
            'INSERT INTO "users" (comment) SELECT post FROM __temp__users',
            'DROP TABLE __temp__users',
        ]

        self.assertEqual(sql, self.platform.compile_alter_sql(diff))

    def test_alter_advanced_rename_columns(self):
        table = Table("users")
        table.add_column("post", "integer")
        table.add_column("user", "integer")
        table.add_column("email", "integer")
        
        diff = TableDiff("users")
        diff.from_table = table
        diff.rename_column("post", "comment", "integer")

        sql = [
            "CREATE TEMPORARY TABLE __temp__users AS SELECT post, user, email FROM users", 
            "DROP TABLE users",
            'CREATE TABLE "users" (comment INTEGER, user INTEGER, email INTEGER)',
            'INSERT INTO "users" (comment, user, email) SELECT post, user, email FROM __temp__users',
            'DROP TABLE __temp__users',
        ]

        self.assertEqual(sql, self.platform.compile_alter_sql(diff))

    def test_alter_rename_column_and_rename_table(self):
        table = Table("users")
        table.add_column("post", "integer")
        
        diff = TableDiff("users")
        diff.from_table = table
        diff.new_name = "clients"
        diff.rename_column("post", "comment", "integer")

        sql = [
            "CREATE TEMPORARY TABLE __temp__users AS SELECT post FROM users", 
            "DROP TABLE users",
            'CREATE TABLE "users" (comment INTEGER)',
            'INSERT INTO "users" (comment) SELECT post FROM __temp__users',
            'DROP TABLE __temp__users',
            "ALTER TABLE users RENAME TO clients"
        ]

        self.assertEqual(sql, self.platform.compile_alter_sql(diff))
