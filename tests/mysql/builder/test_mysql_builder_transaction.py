import inspect
import os
import unittest

from src.masoniteorm.orm.query import QueryBuilder
from src.masoniteorm.orm.query.grammars import MySQLGrammar
from src.masoniteorm.orm.connections import ConnectionFactory
from src.masoniteorm.orm.relationships import belongs_to
from src.masoniteorm.orm.models import Model
from tests.utils import MockConnectionFactory
from config.database import DATABASES

if os.getenv("RUN_MYSQL_DATABASE") == "True":

    class User(Model):
        __connection__ = "mysql"
        __timestamps__ = False

    class BaseTestQueryRelationships(unittest.TestCase):

        maxDiff = None

        def get_builder(self, table="users"):
            connection = ConnectionFactory().make("mysql")
            return QueryBuilder(
                grammar=MySQLGrammar,
                connection=connection,
                table=table,
                # model=User,
                connection_details=DATABASES,
            ).on("mysql")

        def test_transaction(self):
            builder = self.get_builder()
            builder.begin()
            builder.create({"name": "phillip2", "email": "phillip2"})
            # builder.commit()
            user = builder.where("name", "phillip2").first()
            print(user)
            self.assertEqual(user["name"], "phillip2")
            builder.rollback()
            user = builder.where("name", "phillip2").first()
            self.assertEqual(user, None)
