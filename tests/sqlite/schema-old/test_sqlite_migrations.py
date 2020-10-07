import inspect
import unittest

from src.masoniteorm.schema import Schema
from src.masoniteorm.connections import SQLiteConnection
from src.masoniteorm.schema.grammars import SQLiteGrammar
from config.database import DATABASES
import unittest


class BaseTestSqliteMigration(unittest.TestCase):

    maxDiff = None

    schema = Schema(
        connection=SQLiteConnection,
        grammar=SQLiteGrammar,
        connection_details=DATABASES,
        connection_driver="sqlite",
    )

    def test_can_compile_column(self):
        with self.schema.create("testfile4") as blueprint:
            blueprint.string("name")

        self.schema.drop_table_if_exists("testfile4")
