import unittest

from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar
from src.masoniteorm.relationships import belongs_to, has_many, has_one
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import SQLitePlatform
from tests.integrations.config.database import DATABASES


class Logo(Model):
    __connection__ = "dev"


class Article(Model):
    __connection__ = "dev"

    @belongs_to("logo_id", "id")
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

    @has_one("user_id", "id")
    def profile(self):
        return Profile


class EagerUser(Model):
    __connection__ = "dev"
    __with__ = ("profile",)
    __table__ = "users"

    @belongs_to("id", "user_id")
    def profile(self):
        return Profile


class SqliteTestBuilderEagerLoading(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.connection = ConnectionFactory().make("sqlite")
        cls.schema = Schema(
            connection="dev",
            connection_details=DATABASES,
            platform=SQLitePlatform,
        ).on("dev")

        cls.schema.drop_table_if_exists("users")
        with cls.schema.create("users") as table:
            table.integer("id").primary()
            table.string("name")

        cls.schema.drop_table_if_exists("profiles")
        with cls.schema.create("profiles") as table:
            table.integer("id").primary()
            table.integer("user_id")
            table.string("occupation")

        cls.schema.drop_table_if_exists("articles")
        with cls.schema.create("articles") as table:
            table.integer("id").primary()
            table.integer("user_id")
            table.integer("logo_id")
            table.string("name")

        cls.schema.drop_table_if_exists("logos")
        with cls.schema.create("logos") as table:
            table.integer("id").primary()
            table.string("name")

        User.builder.new().bulk_create(
            [
                {"name": "Steve"},
                {"name": "Joe"},
                {"name": "Bob"},
            ]
        )
        Profile.builder.new().bulk_create(
            [
                {"user_id": 1, "occupation": "occupation"},
                {"user_id": 2, "occupation": "occupation"},
                {"user_id": 3, "occupation": "occupation"},
            ]
        )
        Logo.builder.new().bulk_create(
            [
                {"name": "Bing"},
                {"name": "Zap"},
                {"name": "Swoosh"},
            ]
        )
        Article.builder.new().bulk_create(
            [
                {"name": "Article 1", "user_id": 2, "logo_id": 3},
                {"name": "Article 2", "user_id": 2, "logo_id": 1},
                {"name": "Article 3", "user_id": 1, "logo_id": 3},
                {"name": "Article 4", "user_id": 1, "logo_id": 1},
                {"name": "Article 5", "user_id": 3, "logo_id": 3},
            ]
        )

    @classmethod
    def tearDownClass(cls):
        cls.schema.drop_table_if_exists("users")
        cls.schema.drop_table_if_exists("articles")
        cls.schema.drop_table_if_exists("profiles")
        cls.schema.drop_table_if_exists("logos")

    def get_builder(self, table="users", model=User):
        return QueryBuilder(
            grammar=SQLiteGrammar,
            connection="dev",
            connection_class=self.connection,
            table=table,
            model=model(),
            connection_details=DATABASES,
        ).on("dev")

    def test_with(self):
        builder = self.get_builder()
        result = builder.with_("profile").get()
        for model in result:
            if model.profile:
                self.assertEqual(model.profile.occupation, "occupation")

    def test_with_from_model(self):
        result = EagerUser.get()
        for model in result:
            if model.profile:
                self.assertEqual(model.profile.occupation, "occupation")

    def test_with_first(self):
        builder = self.get_builder()
        result = builder.with_("profile").where("id", 1).first()
        self.assertEqual(result.profile.occupation, "occupation")

    def test_with_where_no_relation(self):
        builder = self.get_builder()
        result = (
            builder.with_("profile")
            .where_has("profile", lambda query: (query.where("id", 5)))
            .first()
        )
        self.assertIsNone(result)

    def test_with_multiple_per_same_relation(self):
        result = User.with_("articles", "articles.logo").where("id", 1).first()
        serialized = result.serialize()
        self.assertEqual(len(serialized["articles"]), 2)
        self.assertEqual(serialized["articles"][0]["logo"]["name"], "Swoosh")
