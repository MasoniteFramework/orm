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
        table.add_constraint("name", "unique")

        diff = TableDiff("users")
        diff.from_table = table
        diff.new_name = "clients"
        diff.remove_constraint("name")

        sql = ["ALTER TABLE users RENAME TO clients"]

        self.assertEqual(sql, self.platform.compile_alter_sql(diff))
