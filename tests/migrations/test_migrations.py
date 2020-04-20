import os
import unittest

from src.masonite.orm.migrations.Migration import Migration
from src.masonite.orm.models.MigrationModel import MigrationModel
from inflection import camelize
from pydoc import locate


class TestMigrations(unittest.TestCase):
    def setUp(self):
        pass

    def test_has_migrations(self):
        pass

    def test_migrate(self):
        migration_class = Migration()
        migration_class.create_table_if_not_exists()
        migration_class.migrate()

    def test_rollback(self):
        migration_class = Migration()
        migration_class.create_table_if_not_exists()
        migration_class.rollback()
