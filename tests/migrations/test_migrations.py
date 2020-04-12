import os
import unittest

from src.masonite.orm.migrations.Migration import Migration


class TestMigrations(unittest.TestCase):
    def setUp(self):
        pass

    def test_has_migrations(self):
        print(Migration().create_table_if_not_exists())
