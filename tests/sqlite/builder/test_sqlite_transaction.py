import unittest

from src.masoniteorm.collection import Collection
from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar
from tests.integrations.config.database import DB


class User(Model):
    __connection__ = "dev"
    __timestamps__ = False


class SqliteTestQueryBuilderTransaction(unittest.TestCase):
    maxDiff = None

    def get_builder(self, table="users"):
        connection = ConnectionFactory(resolver=DB).make("sqlite")
        return QueryBuilder(
            grammar=SQLiteGrammar,
            connection_class=connection,
            connection="dev",
            table=table,
            model=User(),
            connection_details=DB.get_connection_details(),
        ).on("dev")

    def test_transaction(self):
        builder = self.get_builder()
        builder.begin()
        builder.create({"name": "phillip3", "email": "phillip3"})
        user = builder.where("name", "phillip3").first()
        self.assertEqual(user["name"], "phillip3")
        builder.rollback()
        user = builder.where("name", "phillip3").first()
        self.assertEqual(user, None)

    def test_transaction_globally(self):
        connection = DB.begin_transaction("dev")
        self.assertEqual(connection, self.get_builder().new_connection())
        DB.commit("dev")
        DB.begin_transaction("dev")
        DB.rollback("dev")

    def test_chunking(self):
        for users in self.get_builder().chunk(10):
            self.assertIsInstance(users, Collection)
