import inspect
import unittest

from tests.integrations.config.database import DATABASES
from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar
from src.masoniteorm.relationships import belongs_to
from tests.utils import MockConnectionFactory
from tests.integrations.config.database import DB


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

    def booted(self, user):
        user.observed_booting = 1

    def booting(self, user):
        user.observed_booted = 1

    def hydrating(self, user):
        user.observed_hydrating = 1

    def hydrated(self, user):
        user.observed_hydrated = 1

    def deleting(self, user):
        user.observed_deleting = 1

    def deleted(self, user):
        user.observed_deleted = 1


class Observer(Model):
    __connection__ = "dev"
    __timestamps__ = False
    __observers__ = {}


Observer.observe(UserObserver())


class BaseTestQueryRelationships(unittest.TestCase):

    maxDiff = None

    def test_created_is_observed(self):
        # DB.begin_transaction("dev")
        user = Observer.create({"name": "joe"})
        self.assertEqual(user.observed_creating, 1)
        self.assertEqual(user.observed_created, 1)
        # DB.rollback("dev")

    def test_saving_is_observed(self):
        # DB.begin_transaction("dev")
        user = Observer.hydrate({"id": 1, "name": "joe"})

        user.name = "bill"
        user.save()

        self.assertEqual(user.observed_saving, 1)
        self.assertEqual(user.observed_saved, 1)
        # DB.rollback("dev")

    def test_updating_is_observed(self):
        # DB.begin_transaction("dev")
        user = Observer.hydrate({"id": 1, "name": "joe"})

        re = user.update({"name": "bill"})

        self.assertEqual(user.observed_updated, 1)
        self.assertEqual(user.observed_updating, 1)
        # DB.rollback("dev")

    def test_booting_is_observed(self):
        # DB.begin_transaction("dev")
        user = Observer.hydrate({"id": 1, "name": "joe"})

        re = user.update({"name": "bill"})

        self.assertEqual(user.observed_booting, 1)
        self.assertEqual(user.observed_booted, 1)
        # DB.rollback("dev")

    def test_deleting_is_observed(self):
        DB.begin_transaction("dev")
        user = Observer.hydrate({"id": 10, "name": "joe"})

        re = user.delete()

        self.assertEqual(user.observed_deleting, 1)
        self.assertEqual(user.observed_deleted, 1)
        DB.rollback("dev")

    def test_hydrating_is_observed(self):
        DB.begin_transaction("dev")
        user = Observer.hydrate({"id": 10, "name": "joe"})

        self.assertEqual(user.observed_hydrating, 1)
        self.assertEqual(user.observed_hydrated, 1)
        DB.rollback("dev")
