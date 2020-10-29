import inspect
import unittest

from config.database import DATABASES
from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.connections.decorators import Transaction as transaction
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


@transaction(connection="sqlite")
def create_user():
    User.create({"name": "phillip2", "email": "phillip3"})

@transaction(connection="sqlite")
def create_user_with_error():
    User.create({"name": "phillip3", "email": "phillip3"})
    raise Exception("error faking")
    User.create({"name": "phillip4", "email": "phillip4"})


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

    def test_transaction_if_sucess(self):
        count = User.all().count()
        create_user()
        assert User.all().count() == count + 1

    def test_transaction_rollback_if_error(self):
        count = User.all().count()
        with self.assertRaises(Exception):
            create_user_with_error()
        # check no users created
        assert User.all().count() == count

    def test_chunking(self):
        for users in self.get_builder().chunk(10):
            self.assertIsInstance(users, Collection)
