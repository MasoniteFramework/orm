import unittest

from src.masoniteorm.models import Model
from src.masoniteorm.query.grammars import SQLiteGrammar
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import SQLitePlatform
from tests.integrations.config.database import DATABASES


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


class DwliteTestObserver(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.schema = Schema(
            grammar=SQLiteGrammar,
            connection="dev",
            connection_details=DATABASES,
            platform=SQLitePlatform,
        ).on("dev")

        with cls.schema.create("observers") as table:
            table.integer("id").primary()
            table.string("name")

    @classmethod
    def tearDownClass(cls):
        cls.schema.drop_table_if_exists("observers")

    def setUp(self):
        self.schema.truncate("observers")

    def test_created_is_observed(self):
        user = Observer.create({"name": "joe"})
        self.assertEqual(TestM.observed_creating, 1)
        self.assertEqual(TestM.observed_created, 1)

    def test_saving_is_observed(self):
        user = Observer.hydrate({"id": 1, "name": "joe"})

        user.name = "bill"
        user.save()

        self.assertEqual(TestM.observed_saving, 1)
        self.assertEqual(TestM.observed_saved, 1)

    def test_updating_is_observed(self):
        user = Observer.hydrate({"id": 1, "name": "joe"})

        user.update({"name": "bill"})

        self.assertEqual(TestM.observed_updated, 1)
        self.assertEqual(TestM.observed_updating, 1)

    def test_booting_is_observed(self):
        user = Observer.hydrate({"id": 1, "name": "joe"})

        user.update({"name": "bill"})

        self.assertEqual(TestM.observed_booting, 1)
        self.assertEqual(TestM.observed_booted, 1)

    def test_deleting_is_observed(self):
        user = Observer.hydrate({"id": 10, "name": "joe"})

        user.delete()

        self.assertEqual(TestM.observed_deleting, 1)
        self.assertEqual(TestM.observed_deleted, 1)

    def test_hydrating_is_observed(self):
        Observer.hydrate({"id": 10, "name": "joe"})

        self.assertEqual(TestM.observed_hydrating, 1)
        self.assertEqual(TestM.observed_hydrated, 1)
