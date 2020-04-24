import os
import unittest

from src.masonite.orm.migrations.Migration import Migration
from src.masonite.orm.models.MigrationModel import MigrationModel
from inflection import camelize
from pydoc import locate


class TestMigrations(unittest.TestCase):
    def setUp(self):
        self.migration = Migration(dry=True)

    def test_has_migrations(self):
        pass

    # def test_migrate(self):
    #     self.migration.create_table_if_not_exists()
    #     self.migration.migrate()
    #     self.assertEqual(
    #         self.migration.last_migrations_ran,
    #         [
    #             "2020_04_17_000000_create_friends_table.py",
    #             "2020_04_17_00000_create_articles_table.py",
    #         ],
    #     )
