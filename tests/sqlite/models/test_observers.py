import inspect
import unittest

from config.database import DATABASES
from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar
from src.masoniteorm.relationships import belongs_to
from tests.utils import MockConnectionFactory
from config.database import db


class UserObserver:
    def created(self, user):
        user.observed_created = 1

    def creating(self, user):
        user.observed_creating = 1

    def saving(self, user):
        user.observed_saving = 1

    def saved(self, user):
        user.observed_saved = 1

    def updating(self, user):
        user.observed_updating = 1

    def updated(self, user):
        user.observed_updated = 1


class Observer(Model):
    __connection__ = "sqlite"
    __timestamps__ = False
    __observers__ = [UserObserver()]

    # __dry__ = True


class BaseTestQueryRelationships(unittest.TestCase):

    maxDiff = None

    def test_created_is_observed(self):
        # db.begin_transaction("sqlite")
        user = Observer.create({"name": "joe"})
        self.assertEqual(user.observed_creating, 1)
        self.assertEqual(user.observed_created, 1)
        # db.rollback("sqlite")

    def test_saving_is_observed(self):
        # db.begin_transaction("sqlite")
        user = Observer.hydrate({"id": 1, "name": "joe"})

        user.name = "bill"
        user.save()

        self.assertEqual(user.observed_saving, 1)
        self.assertEqual(user.observed_saved, 1)
        # db.rollback("sqlite")

    def test_updating_is_observed(self):
        # db.begin_transaction("sqlite")
        user = Observer.hydrate({"id": 1, "name": "joe"})

        re = user.update({"name": "bill"})

        self.assertEqual(user.observed_updated, 1)
        self.assertEqual(user.observed_updating, 1)
        # db.rollback("sqlite")
