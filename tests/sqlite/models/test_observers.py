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


class TestM:
    pass


class UserObserver:
    def created(self, user):
        TestM.observed_created = 1

    def creating(self, user):
        TestM.observed_creating = 1

    def saving(self, user):
        TestM.observed_saving = 1

    def saved(self, user):
        TestM.observed_saved = 1

    def updating(self, user):
        TestM.observed_updating = 1

    def updated(self, user):
        TestM.observed_updated = 1

    def booted(self, user):
        TestM.observed_booting = 1

    def booting(self, user):
        TestM.observed_booted = 1

    def hydrating(self, user):
        TestM.observed_hydrating = 1

    def hydrated(self, user):
        TestM.observed_hydrated = 1

    def deleting(self, user):
        TestM.observed_deleting = 1

    def deleted(self, user):
        TestM.observed_deleted = 1


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
        self.assertEqual(TestM.observed_creating, 1)
        self.assertEqual(TestM.observed_created, 1)
        # DB.rollback("dev")

    def test_saving_is_observed(self):
        # DB.begin_transaction("dev")
        user = Observer.hydrate({"id": 1, "name": "joe"})

        user.name = "bill"
        user.save()

        self.assertEqual(TestM.observed_saving, 1)
        self.assertEqual(TestM.observed_saved, 1)
        # DB.rollback("dev")

    def test_updating_is_observed(self):
        # DB.begin_transaction("dev")
        user = Observer.hydrate({"id": 1, "name": "joe"})

        re = user.update({"name": "bill"})

        self.assertEqual(TestM.observed_updated, 1)
        self.assertEqual(TestM.observed_updating, 1)
        # DB.rollback("dev")

    def test_booting_is_observed(self):
        # DB.begin_transaction("dev")
        user = Observer.hydrate({"id": 1, "name": "joe"})

        re = user.update({"name": "bill"})

        self.assertEqual(TestM.observed_booting, 1)
        self.assertEqual(TestM.observed_booted, 1)
        # DB.rollback("dev")

    def test_deleting_is_observed(self):
        DB.begin_transaction("dev")
        user = Observer.hydrate({"id": 10, "name": "joe"})

        re = user.delete()

        self.assertEqual(TestM.observed_deleting, 1)
        self.assertEqual(TestM.observed_deleted, 1)
        DB.rollback("dev")

    def test_hydrating_is_observed(self):
        DB.begin_transaction("dev")
        user = Observer.hydrate({"id": 10, "name": "joe"})

        self.assertEqual(TestM.observed_hydrating, 1)
        self.assertEqual(TestM.observed_hydrated, 1)
        DB.rollback("dev")

    def test_model_can_observe_callback(self):
        events = {
            "creating": False,
            "created": False,
            "deleting": False,
            "deleted": False,
            "hydrating": False,
            "hydrated": False,
            "saving": False,
            "saved": False,
            "updating": False,
            "updated": False,
        }
        class ModelWithCallbacksObserver(Model):
            def booted(cls):
                cls.creating(lambda m: events.update({"creating": True}))
                cls.created(lambda m: events.update({"created": True}))
                cls.deleting(lambda m: events.update({"deleting": True}))
                cls.deleted(lambda m: events.update({"deleted": True}))
                cls.hydrating(lambda m: events.update({"hydrating": True}))
                cls.hydrated(lambda m: events.update({"hydrated": True}))
                cls.saving(lambda m: events.update({"saving": True}))
                cls.saved(lambda m: events.update({"saved": True}))
                cls.updating(lambda m: events.update({"updating": True}))
                cls.updated(lambda m: events.update({"updated": True}))

        model = ModelWithCallbacksObserver()
        for event in events:
            model.observe_events(model, event)

        for event, is_called in events.items():
            self.assertTrue(is_called)

    def test_model_can_observe_two_callbacks_on_same_event(self):
        creating_called_num  = 0
        def callback(_):
            nonlocal creating_called_num
            creating_called_num += 1

        class ModelWithCallbacksObserver(Model):
            def booted(cls):
                cls.creating(callback)
                cls.creating(callback)

        model = ModelWithCallbacksObserver()
        model.observe_events(model, 'creating')

        self.assertEqual(2, creating_called_num)