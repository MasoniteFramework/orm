import unittest

from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import SQLitePlatform
from tests.integrations.config.database import DATABASES


class User(Model):
    __connection__ = "dev"
    __timestamps__ = False
    pass


class SqliteTestBuilderInsert(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.connection = ConnectionFactory().make("sqlite")
        cls.schema = Schema(
            connection="dev",
            connection_class=cls.connection,
            connection_details=DATABASES,
            platform=SQLitePlatform,
        ).on("dev")

        with cls.schema.create("users") as table:
            table.integer("id").primary()
            table.string("name")
            table.string("email")
            table.string("password")

    @classmethod
    def tearDownClass(cls):
        cls.schema.drop_table_if_exists("users")

    def get_builder(self, table="users"):
        return QueryBuilder(
            grammar=SQLiteGrammar,
            connection_class=self.connection,
            connection="dev",
            table=table,
            connection_details=DATABASES,
        ).on("dev")

    def test_insert(self):
        builder = self.get_builder()
        result = builder.create(
            {"name": "Joe", "email": "joe@masoniteproject.com", "password": "secret"}
        )

        self.assertIsInstance(result["id"], int)
