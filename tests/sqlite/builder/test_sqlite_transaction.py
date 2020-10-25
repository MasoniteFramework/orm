import inspect
import unittest

from config.database import DATABASES
from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.connections.decorators import transaction
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar
from src.masoniteorm.relationships import belongs_to
from tests.utils import MockConnectionFactory
from config.database import db
from src.masoniteorm.collection import Collection


class User(Model):
    __connection__ = "sqlite"
    __timestamps__ = False


class BaseTestQueryRelationships(unittest.TestCase):

    maxDiff = None

    def get_builder(self, table="users"):
        connection = ConnectionFactory().make("sqlite")
        return QueryBuilder(
            grammar=SQLiteGrammar,
            connection=connection,
            table=table,
            model=User,
            connection_details=DATABASES,
        ).on("sqlite")

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
        connection = db.begin_transaction("sqlite")
        self.assertEqual(connection, self.get_builder().new_connection())
        db.commit("sqlite")
        db.begin_transaction("sqlite")
        db.rollback("sqlite")

    def test_transaction_decorator(self):
        @transaction(connection="sqlite")
        def create_user():
            User.create({"name": "phillip3", "email": "phillip3"})

        create_user()
        db.rollback("sqlite")

    def test_chunking(self):
        for users in self.get_builder().chunk(10):
            self.assertIsInstance(users, Collection)
