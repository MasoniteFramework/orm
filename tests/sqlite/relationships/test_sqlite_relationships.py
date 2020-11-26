import os
import unittest

from src.masoniteorm.models import Model
from src.masoniteorm.relationships import belongs_to, has_many
from config.database import DB


class Profile(Model):
    __table__ = "profiles"
    __connection__ = "sqlite"


class Articles(Model):
    __table__ = "articles"
    __connection__ = "sqlite"
    __timestamps__ = None

    @belongs_to("id", "article_id")
    def logo(self):
        return Logo


class Logo(Model):
    __table__ = "logos"
    __connection__ = "sqlite"
    __timestamps__ = None


class User(Model):

    __connection__ = "sqlite"

    _eager_loads = ()

    __casts__ = {"is_admin": "bool"}

    @belongs_to("id", "user_id")
    def profile(self):
        return Profile

    @has_many("id", "user_id")
    def articles(self):
        return Articles

    def get_is_admin(self):
        return "You are an admin"


class TestRelationships(unittest.TestCase):
    maxDiff = None

    def test_relationship_can_be_callable(self):
        self.assertEqual(
            User.profile().where("name", "Joe").to_sql(),
            """SELECT * FROM "profiles" WHERE "profiles"."name" = 'Joe'""",
        )

    def test_can_access_relationship(self):
        for user in User.where("id", 1).get():
            self.assertIsInstance(user.profile, Profile)

    def test_can_access_has_many_relationship(self):
        user = User.hydrate(User.where("id", 1).first())
        self.assertEqual(len(user.articles), 1)

    def test_can_access_relationship_multiple_times(self):
        user = User.hydrate(User.where("id", 1).first())
        self.assertEqual(len(user.articles), 1)
        self.assertEqual(len(user.articles), 1)

    def test_loading(self):
        users = User.with_("articles").get()
        for user in users:
            user

    def test_loading_with_nested_with(self):
        users = User.with_("articles", "articles.logo").get()
        for user in users:
            for article in user.articles:
                if article.logo:
                    print("aa", article.logo.url)

    def test_casting(self):
        users = User.with_("articles").where("is_admin", True).get()
        for user in users:
            user

    def test_setting(self):
        users = User.with_("articles").where("is_admin", True).get()
        for user in users:
            user.name = "Joe"
            user.is_admin = 1
            user.save()

    def test_related(self):
        user = User.first()
        related_query = user.related("profile").where("active", 1).to_sql()
        self.assertEqual(
            related_query,
            """SELECT * FROM "profiles" WHERE "profiles"."user_id" = '1' AND "profiles"."active" = '1'""",
        )

    def test_associate_records(self):
        db.begin_transaction("sqlite")
        user = User.first()

        articles = [Articles.hydrate({"title": "associate records"})]

        user.save_many("articles", articles)
        db.rollback("sqlite")

    def test_attach_records(self):
        db.begin_transaction("sqlite")
        article = Articles.first()

        logo = Logo.hydrate({"url": "yahoo.com"})

        article.attach("logo", logo)
        db.rollback("sqlite")
