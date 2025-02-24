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

    def setUp(self):
        self.schema.truncate("users")

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

    def test_transaction_commit(self):
        builder = self.get_builder()
        builder.begin()
        try:
            builder.create(
                {"name": "phillip3", "email": "phillip3", "password": "secret"}
            )
            builder.commit()
        except Exception as e:
            builder.rollback()
            self.assertEqual(str(e), "")

        user = builder.where("name", "phillip3").first()
        self.assertEqual(user["name"], "phillip3")

    def test_transaction_rollback(self):
        builder = self.get_builder()
        builder.begin()
        try:
            builder.create(
                {"name": "phillip3", "email": "phillip3", "password": "secret"}
            )
            user = builder.where("name", "phillip3").first()
            self.assertEqual(user["name"], "phillip3")
        except Exception as e:
            builder.rollback()
            self.assertEqual(str(e), "")

        builder.rollback()
        user = builder.where("name", "phillip3").first()
        self.assertEqual(user, None)

    def test_transaction_globally_coimmit(self):
        builder = self.get_builder()
        connection = DB.begin_transaction(builder.connection)
        self.assertEqual(connection, builder.new_connection())
        try:
            builder.create(
                {"name": "phillip3", "email": "phillip3", "password": "secret"}
            )
            DB.commit(builder.connection)
        except Exception as e:
            DB.rollback(builder.connection)
            self.assertEqual(str(e), "")

        user = builder.where("name", "phillip3").first()
        self.assertEqual(user["name"], "phillip3")

    def test_transaction_globally_rollback(self):
        builder = self.get_builder()
        connection = DB.begin_transaction(builder.connection)
        self.assertEqual(connection, builder.new_connection())
        try:
            builder.create(
                {"name": "phillip3", "email": "phillip3", "password": "secret"}
            )
            user = builder.where("name", "phillip3").first()
            self.assertEqual(user["name"], "phillip3")
        except Exception as e:
            DB.rollback(builder.connection)
            self.assertEqual(str(e), "")

        DB.rollback(builder.connection)
        user = builder.where("name", "phillip3").first()
        self.assertEqual(user, None)

    def test_chunking(self):
        for users in self.get_builder().chunk(10):
            self.assertIsInstance(users, Collection)
