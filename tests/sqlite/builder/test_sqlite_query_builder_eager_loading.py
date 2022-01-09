import inspect
import unittest

from tests.integrations.config.database import DATABASES
from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar
from src.masoniteorm.relationships import belongs_to, has_many
from tests.utils import MockConnectionFactory


class Logo(Model):
    __connection__ = "dev"


class Article(Model):
    __connection__ = "dev"

    @belongs_to("id", "article_id")
    def logo(self):
        return Logo

    @belongs_to("user_id", "id")
    def user(self):
        return User


class Profile(Model):
    __connection__ = "dev"


class User(Model):
    __connection__ = "dev"

    __with__ = ["articles.logo"]

    @has_many("id", "user_id")
    def articles(self):
        return Article

    @belongs_to("id", "user_id")
    def profile(self):
        return Profile


class EagerUser(Model):
    __connection__ = "dev"

    __with__ = ("profile",)
    __table__ = "users"

    @belongs_to("id", "user_id")
    def profile(self):
        return Profile


class BaseTestQueryRelationships(unittest.TestCase):

    maxDiff = None

    def get_builder(self, table="users", model=User):
        connection = ConnectionFactory().make("sqlite")
        return QueryBuilder(
            grammar=SQLiteGrammar,
            connection="dev",
            table=table,
            model=model,
            connection_details=DATABASES,
        ).on("dev")

    def test_with(self):
        builder = self.get_builder()
        result = builder.with_("profile").get()
        for model in result:
            if model.profile:
                self.assertEqual(model.profile.title, "title")

    def test_with_from_model(self):
        builder = EagerUser
        result = builder.get()
        for model in result:
            if model.profile:
                self.assertEqual(model.profile.title, "title")

    def test_with_first(self):
        builder = self.get_builder()
        result = builder.with_("profile").where("id", 1).first()
        self.assertEqual(result.profile.title, "title")

    def test_with_where_no_relation(self):
        builder = self.get_builder()
        result = builder.with_("profile").where("id", 5).first()
        result.serialize()

    def test_with_multiple_per_same_relation(self):
        builder = self.get_builder()
        result = User.with_("articles", "articles.logo").where("id", 1).first()
        self.assertTrue(result.serialize()["articles"])
        self.assertTrue(result.serialize()["articles"][0]["logo"])
