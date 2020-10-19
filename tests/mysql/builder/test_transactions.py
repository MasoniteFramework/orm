import inspect
import os
import unittest

from src.masoniteorm.connections.ConnectionFactory import ConnectionFactory
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import MySQLGrammar
from src.masoniteorm.relationships import has_many
from tests.utils import MockConnectionFactory


class Articles(Model):
    pass


class User(Model):
    @has_many("id", "user_id")
    def articles(self):
        return Articles


if os.getenv("RUN_MYSQL_DATABASE", False) == "True":

    class TestTransactions(unittest.TestCase):
        pass
        # def get_builder(self, table="users"):
        #     connection = ConnectionFactory().make("default")
        #     return QueryBuilder(MySQLGrammar, connection, table=table, model=User)

        # def test_can_start_transaction(self, table="users"):
        #     builder = self.get_builder()
        #     builder.begin()
        #     builder.create({"name": "mike", "email": "mike@email.com"})
        #     builder.rollback()
        # self.assertFalse(builder.where("email", "mike@email.com").first())
