import unittest

from src.masoniteorm.collection import Collection
from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import SQLitePlatform
from tests.integrations.config.database import DATABASES, DB


class User(Model):
    __connection__ = "dev"
    __timestamps__ = False


class SqliteTestTransaction(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.connection = ConnectionFactory().make("sqlite")
        cls.schema = Schema(
            grammar=SQLiteGrammar,
            connection="dev",
            # connection_class=cls.connection,
            connection_details=DATABASES,
            platform=SQLitePlatform,
        ).on("dev")

        cls.schema.drop_table_if_exists("users")
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
            model=User(),
            connection_details=DATABASES,
        ).on("dev")

    # def test_transaction(self):
    #     builder = self.get_builder()
    #     builder.begin()
    #     builder.create({"name": "phillip3", "email": "phillip3"})
    #     user = builder.where("name", "phillip3").first()
    #     self.assertEqual(user["name"], "phillip3")
    #     builder.rollback()
    #     user = builder.where("name", "phillip3").first()
    #     self.assertEqual(user, None)

    def test_transaction_globally(self):
        connection = DB.begin_transaction("dev")
        self.assertEqual(connection, self.get_builder().new_connection())
        DB.commit("dev")
        DB.begin_transaction("dev")
        DB.rollback("dev")

    def test_chunking(self):
        for users in self.get_builder().chunk(10):
            self.assertIsInstance(users, Collection)
