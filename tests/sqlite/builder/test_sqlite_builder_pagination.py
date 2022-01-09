import inspect
import unittest

from tests.integrations.config.database import DATABASES
from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar
from src.masoniteorm.relationships import belongs_to
from tests.utils import MockConnectionFactory


class User(Model):
    __connection__ = "dev"


class BaseTestQueryRelationships(unittest.TestCase):

    maxDiff = None

    def get_builder(self, table="users", model=User):
        connection = ConnectionFactory().make("sqlite")
        return QueryBuilder(
            grammar=SQLiteGrammar,
            connection_class=connection,
            connection="dev",
            table=table,
            model=model,
            connection_details=DATABASES,
        ).on("dev")

    def test_pagination(self):
        builder = self.get_builder()

        paginator = builder.table("users").paginate(1)

        self.assertTrue(paginator.count)
        self.assertTrue(paginator.serialize()["data"])
        self.assertTrue(paginator.serialize()["meta"])
        self.assertTrue(paginator.result)
        self.assertTrue(paginator.current_page)
        self.assertTrue(paginator.per_page)
        self.assertTrue(paginator.count)
        self.assertTrue(paginator.last_page)
        self.assertTrue(paginator.next_page)
        self.assertEqual(paginator.previous_page, None)
        self.assertTrue(paginator.total)
        for user in paginator:
            self.assertIsInstance(user, User)

        paginator = builder.table("users").simple_paginate(10, 1)

        self.assertIsInstance(paginator.to_json(), str)

        self.assertTrue(paginator.count)
        self.assertTrue(paginator.serialize()["data"])
        self.assertTrue(paginator.serialize()["meta"])
        self.assertTrue(paginator.result)
        self.assertTrue(paginator.current_page)
        self.assertTrue(paginator.per_page)
        self.assertTrue(paginator.count)
        self.assertEqual(paginator.next_page, None)
        self.assertEqual(paginator.previous_page, None)
        for user in paginator:
            self.assertIsInstance(user, User)

        self.assertIsInstance(paginator.to_json(), str)
