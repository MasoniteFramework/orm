import inspect
import unittest

from config.database import DATABASES
from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar
from src.masoniteorm.relationships import belongs_to
from tests.utils import MockConnectionFactory


class User(Model):
    __connection__ = "sqlite"
    __timestamps__ = False
    pass


class BaseTestQueryRelationships(unittest.TestCase):

    maxDiff = None

    def get_builder(self, table="users"):
        connection = ConnectionFactory().make("sqlite")
        return QueryBuilder(
            grammar=SQLiteGrammar,
            connection=connection,
            table=table,
            # model=User,
            connection_details=DATABASES,
        ).on("sqlite")

    def test_insert(self):
        builder = self.get_builder()
        result = builder.create(
            {"name": "Joe", "email": "joe@masoniteproject.com", "password": "secret"}
        )

        self.assertIsInstance(result["id"], int)
