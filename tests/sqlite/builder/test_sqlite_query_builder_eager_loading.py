import inspect
import unittest

from src.masoniteorm.orm.query import QueryBuilder
from src.masoniteorm.orm.query.grammars import SQLiteGrammar
from src.masoniteorm.orm.connections import ConnectionFactory
from src.masoniteorm.orm.models import Model
from src.masoniteorm.orm.relationships import belongs_to
from tests.utils import MockConnectionFactory
from config.database import DATABASES


class Logo(Model):
    __connection__ = "sqlite"


class Article(Model):
    __connection__ = "sqlite"

    @belongs_to("id", "article_id")
    def logo(self):
        return Logo


class Profile(Model):
    __connection__ = "sqlite"


class User(Model):
    __connection__ = "sqlite"

    @belongs_to("id", "user_id")
    def articles(self):
        return Article

    @belongs_to("id", "user_id")
    def profile(self):
        return Profile


class BaseTestQueryRelationships(unittest.TestCase):

    maxDiff = None

    def get_builder(self, table="users"):
        connection = ConnectionFactory().make("sqlite")
        return QueryBuilder(
            grammar=SQLiteGrammar,
            connection=connection,
            table=table,
            model=User,
            connection_details=DATABASES,
        ).on("sqlite")

    def test_with(self):
        builder = self.get_builder()
        result = builder.with_("profile").get()
        for model in result:
            print("rrr", model._relationships)

    def test_with_first(self):
        builder = self.get_builder()
        result = builder.with_("profile").where("id", 2).first()
        self.assertEqual(result.profile.title, "title")
