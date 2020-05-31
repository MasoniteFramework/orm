import inspect
import unittest
import os

from src.masonite.orm.connections.ConnectionFactory import ConnectionFactory

from src.masonite.orm.builder import QueryBuilder
from src.masonite.orm.grammar import MySQLGrammar
from src.masonite.orm.models import Model
from src.masonite.orm.relationships import has_many
from tests.utils import MockConnectionFactory


class Articles(Model):
    pass


class User(Model):
    @has_many("id", "user_id")
    def articles(self):
        return Articles


if os.getenv("RUN_MYSQL_DATABASE", False) == "True":

    class TestTransactions(unittest.TestCase):
        def get_builder(self, table="users"):
            connection = ConnectionFactory().make("default")
            return QueryBuilder(MySQLGrammar, connection, table=table, owner=User)

        def test_can_start_transaction(self, table="users"):
            builder = self.get_builder()
            builder.begin()
            builder.create({"name": "mike", "email": "mike@email.com"})
            builder.rollback()
            self.assertFalse(builder.where("email", "mike@email.com").first())
