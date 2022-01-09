import os
import unittest

from src.masoniteorm.models import Model
from src.masoniteorm.relationships import belongs_to, has_many, has_one, belongs_to_many
from tests.integrations.config.database import DB


class Profile(Model):
    __table__ = "profiles"
    __connection__ = "dev"


class Articles(Model):
    __table__ = "articles"
    __connection__ = "dev"
    __timestamps__ = None
    __dates__ = ["published_date"]

    @belongs_to("id", "article_id")
    def logo(self):
        return Logo


class Logo(Model):
    __table__ = "logos"
    __connection__ = "dev"
    __timestamps__ = None
    __dates__ = ["published_date"]


class User(Model):

    __connection__ = "dev"

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


class Store(Model):

    __connection__ = "dev"

    @belongs_to_many("store_id", "product_id", "id", "id", with_timestamps=True)
    def products(self):
        return Product

    @belongs_to_many("store_id", "product_id", "id", "id", table="product_table")
    def products_table(self):
        return Product

    @belongs_to_many
    def store_products(self):
        return Product


class Product(Model):

    __connection__ = "dev"


class UserHasOne(Model):

    __table__ = "users"

    __connection__ = "dev"

    @has_one("user_id", "user_id")
    def profile(self):
        return Profile


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

    def test_can_access_relationship_date(self):
        user = User.with_("articles").where("id", 1).first()
        for article in user.articles:
            print(article.logo.published_date.is_past())

    def test_loading(self):
        users = User.with_("articles").get()
        for user in users:
            user

    def test_relationship_has_one_sql(self):
        self.assertEqual(UserHasOne.profile().to_sql(), 'SELECT * FROM "profiles"')

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
        DB.begin_transaction("dev")
        user = User.first()

        articles = [Articles.hydrate({"title": "associate records"})]

        user.save_many("articles", articles)
        DB.rollback("dev")

    def test_attach_records(self):
        DB.begin_transaction("dev")
        article = Articles.first()

        logo = Logo.hydrate({"url": "yahoo.com"})

        article.attach("logo", logo)
        DB.rollback("dev")

    def test_belongs_to_many(self):
        store = Store.hydrate({"id": 2, "name": "Walmart"})
        self.assertEqual(store.products.count(), 3)
        self.assertEqual(store.products.serialize()[0]["id"], 4)
        self.assertEqual(store.products.serialize()[0]["name"], "Handgun")
        self.assertEqual(
            store.products.serialize()[0]["updated_at"], "2020-01-01T00:00:00+00:00"
        )
        self.assertEqual(
            store.products.serialize()[0]["created_at"], "2020-01-01T00:00:00+00:00"
        )

    def test_belongs_to_eager_many(self):
        store = Store.hydrate({"id": 2, "name": "Walmart"})
        store = Store.with_("products").first()
        self.assertEqual(store.products.count(), 3)
