import inspect
import unittest

from src.masoniteorm.orm.query import QueryBuilder
from src.masoniteorm.orm.query.grammars import SQLiteGrammar
from src.masoniteorm.orm.connections import ConnectionFactory
from src.masoniteorm.orm.relationships import belongs_to
from src.masoniteorm.orm.models import Model
from tests.utils import MockConnectionFactory
from config.database import DATABASES


class User(Model):
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
                {
                    "name": "Joe",
                    "email": "joe@masoniteproject.com",
                    "password": "secret",
                }
            )

        self.assertIsInstance(result['id'], int)
