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
    __connection__ = "dev"
    __timestamps__ = False
    __dry__ = True


class BaseTestQueryRelationships(unittest.TestCase):

    maxDiff = None

    def test_update_specific_record(self):
        user = User.first()
        sql = user.update({"name": "joe"}).to_sql()

        self.assertEqual(
            sql,
            """UPDATE "users" SET "name" = 'joe' WHERE "id" = '{}'""".format(user.id),
        )

    def test_update_all_records(self):
        sql = User.update({"name": "joe"}).to_sql()

        self.assertEqual(sql, """UPDATE "users" SET "name" = 'joe'""")

    def test_can_find_list(self):
        sql = User.find(1, query=True)

        self.assertEqual(sql, """SELECT * FROM "users" WHERE "users"."id" = '1'""")

        sql = User.find([1, 2, 3], query=True)

        self.assertEqual(
            sql, """SELECT * FROM "users" WHERE "users"."id" IN ('1','2','3')"""
        )

    def test_can_set_and_retreive_attribute(self):
        user = User.hydrate({"id": 1, "name": "joe", "customer_id": 1})
        user.customer_id = "CUST1"
        self.assertEqual(user.customer_id, "CUST1")

