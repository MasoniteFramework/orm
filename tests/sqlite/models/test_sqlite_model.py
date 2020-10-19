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
