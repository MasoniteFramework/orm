import inspect
import unittest

from config.database import DATABASES
from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar
from src.masoniteorm.relationships import belongs_to
from tests.utils import MockConnectionFactory


class UserObserver:
    def created(self, user):
        user.observed = True

    def creating(self, user):
        user.creating = True


class User(Model):
    __connection__ = "sqlite"
    __timestamps__ = False
    __observers__ = [UserObserver()]
    __dry__ = True


class BaseTestQueryRelationships(unittest.TestCase):

    maxDiff = None

    def test_created_is_observed(self):
        user = User.create({"username": "joe"})
        self.assertTrue(user.observed)

    def test_creating_is_observed(self):
        user = User.create({"username": "joe"})
        self.assertTrue(user.creating)
