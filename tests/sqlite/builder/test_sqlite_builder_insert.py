import unittest

from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar
from tests.integrations.config.database import DATABASES


class User(Model):
    __connection__ = "dev"
    __timestamps__ = False
    pass


class BaseTestQueryRelationships(unittest.TestCase):
    maxDiff = None

    def get_builder(self, table="users"):
        connection = ConnectionFactory().make("sqlite")
        return QueryBuilder(
            grammar=SQLiteGrammar,
            connection_class=connection,
            connection="dev",
            table=table,
            connection_details=DATABASES,
        ).on("dev")

    def test_insert(self):
        builder = self.get_builder()
        result = builder.create(
            {
                "name": "Joe",
                "email": "joe@masoniteproject.com",
                "password": "secret",
            }
        )

        self.assertIsInstance(result["id"], int)
