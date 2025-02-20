import unittest

from src.masoniteorm.models import Model
from src.masoniteorm.relationships import belongs_to, morph_to
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import SQLitePlatform
from tests.integrations.config.database import DATABASES, DB


class Profile(Model):
    __table__ = "profiles"
    __connection__ = "dev"


class Articles(Model):
    __table__ = "articles"
    __connection__ = "dev"

    @belongs_to("id", "article_id")
    def logo(self):
        return Logo


class Logo(Model):
    __table__ = "logos"
    __connection__ = "dev"


class Like(Model):
    __connection__ = "dev"

    @morph_to("record_type", "record_id")
    def record(self):
        return self


class User(Model):
    __connection__ = "dev"
    _eager_loads = ()


DB.morph_map({"user": User, "article": Articles})


class TestRelationships(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.schema = Schema(
            connection="dev",
            connection_details=DATABASES,
            platform=SQLitePlatform,
        ).on("dev")

        cls.schema.drop_table_if_exists("users")
        with cls.schema.create("users") as table:
            table.integer("id").primary()
            table.boolean("is_admin").default(False)
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

        cls.schema.drop_table_if_exists("likes")
        with cls.schema.create("likes") as table:
            table.integer("id").primary()
            table.string("record_type")
            table.integer("record_id")

    @classmethod
    def tearDownClass(cls):
        cls.schema.drop_table_if_exists("users")
        cls.schema.drop_table_if_exists("profiles")
        cls.schema.drop_table_if_exists("articles")
        cls.schema.drop_table_if_exists("logos")
        cls.schema.drop_table_if_exists("likes")

    def test_can_get_polymorphic_relation(self):
        likes = Like.get()
        for like in likes:
            self.assertIsInstance(like.record, (Articles, User))

    def test_can_get_eager_load_polymorphic_relation(self):
        likes = Like.with_("record").get()
        for like in likes:
            self.assertIsInstance(like.record, (Articles, User))
