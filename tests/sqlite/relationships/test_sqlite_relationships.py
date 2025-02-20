import unittest

from build.lib.masoniteorm.query import QueryBuilder
from src.masoniteorm.models import Model
from src.masoniteorm.relationships import belongs_to, belongs_to_many, has_many, has_one
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import SQLitePlatform
from tests.integrations.config.database import DATABASES


class Profile(Model):
    __table__ = "profiles_rel"
    __connection__ = "dev"

    @belongs_to(None, "user_id", "id")
    def user(self):
        return User


class Article(Model):
    __table__ = "articles_rel"
    __connection__ = "dev"
    __timestamps__ = None
    __dates__ = ["published_date"]

    @belongs_to(None, "logo_id", "id")
    def logo(self):
        return Logo

    @belongs_to(None, "user_id", "id")
    def user(self):
        return User


class Logo(Model):
    __table__ = "logos_rel"
    __connection__ = "dev"
    __timestamps__ = None
    __dates__ = ["published_date"]


class User(Model):
    __tablename__ = "users_rel"
    __connection__ = "dev"
    _eager_loads = ()
    __timestamps__ = None
    __dry__ = True
    __casts__ = {"is_admin": "bool"}

    @has_many(None, "id", "user_id")
    def articles(self):
        return Article

    @has_one(None, "user_id", "id")
    def profile(self):
        return Profile

    def get_is_admin(self):
        return "You are an admin"


class Store(Model):
    __connection__ = "dev"

    @belongs_to_many("store_id", "product_id", "id", "id", with_timestamps=True)
    def products(self):
        return Product

    @belongs_to_many(None, "store_id", "product_id", "id", "id", table="product_table")
    def products_table(self):
        return Product

    @belongs_to_many
    def store_products(self):
        return Product


class Product(Model):
    __connection__ = "dev"


class SqliteTestRelationships(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.dev_builder = QueryBuilder().on("dev")
        cls.schema = Schema(
            connection="dev",
            connection_details=DATABASES,
            platform=SQLitePlatform,
        ).on("dev")

        cls.schema.drop_table_if_exists("users_rel")
        with cls.schema.create("users_rel") as table:
            table.integer("id").primary()
            table.boolean("is_admin").default(False)
            table.string("name")

        cls.schema.drop_table_if_exists("profiles_rel")
        with cls.schema.create("profiles_rel") as table:
            table.integer("id").primary()
            table.integer("user_id")
            table.string("occupation")

        cls.schema.drop_table_if_exists("articles_rel")
        with cls.schema.create("articles_rel") as table:
            table.integer("id").primary()
            table.integer("user_id")
            table.integer("logo_id", nullable=True)
            table.string("name")

        cls.schema.drop_table_if_exists("logos_rel")
        with cls.schema.create("logos_rel") as table:
            table.integer("id").primary()
            table.string("name")
            table.string("published_date", nullable=True)

        cls.schema.drop_table_if_exists("products")
        with cls.schema.create("products") as table:
            table.integer("id").primary()

        cls.schema.drop_table_if_exists("stores")
        with cls.schema.create("stores") as table:
            table.integer("id").primary()

        cls.schema.drop_table_if_exists("product_store")
        with cls.schema.create("stores") as table:
            table.integer("id").primary()
            table.integer("product_id")
            table.integer("store_id")

    # @classmethod
    # def tearDownClass(cls):
    #     cls.schema.drop_table_if_exists("users_rel")
    #     cls.schema.drop_table_if_exists("profiles_rel")
    #     cls.schema.drop_table_if_exists("articles_rel")
    #     cls.schema.drop_table_if_exists("logos_rel")
    #     cls.schema.drop_table_if_exists("products")
    #     cls.schema.drop_table_if_exists("stores")
    #     cls.schema.drop_table_if_exists("product_store")

    def setUp(self):
        # create minimal data for each test
        User.builder.new().bulk_create(
            [
                {"name": "Steve", "is_admin": False},
                {"name": "Joe", "is_admin": True},
                {"name": "Ed", "is_admin": False},
            ]
        )
        Profile.builder.new().bulk_create(
            [
                {"user_id": 1, "occupation": "Scientist"},
                {"user_id": 2, "occupation": "Developer"},
                {"user_id": 3, "occupation": "Politician"},
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
                {
                    "user_id": 2,
                    "name": "Building Applications with the Masonite Framework",
                    "logo_id": 2,
                },
                {"user_id": 1, "name": "Using a Microscope", "logo_id": 1},
            ]
        )

        Product.builder.new().bulk_create(
            [
                {"name": "Pants"},
                {"name": "Shirt"},
                {"name": "Socks"},
                {"name": "Cup"},
                {"name": "Plate"},
            ]
        )
        Store.builder.new().bulk_create(
            [
                {"name": "K-Mart"},
                {"name": "Target"},
                {"name": "Costco"},
                {"name": "Walmart"},
            ]
        )
        builder = QueryBuilder().on("dev")
        builder.table("product_store").bulk_create(
            [
                {"product_id": 1, "store_id": 2},
                {"product_id": 2, "store_id": 3},
                {"product_id": 3, "store_id": 1},
                {"product_id": 4, "store_id": 4},
                {"product_id": 5, "store_id": 4},
                {"product_id": 2, "store_id": 4},
                {"product_id": 4, "store_id": 1},
                {"product_id": 1, "store_id": 1},
            ]
        )

    def tearDown(self):
        self.schema.truncate("users_rel")
        self.schema.truncate("profiles_rel")
        self.schema.truncate("articles_rel")
        self.schema.truncate("logos_rel")
        self.schema.truncate("products")
        self.schema.truncate("stores")
        self.schema.truncate("product_store")

    def test_relationship_can_be_callable(self):
        self.assertEqual(
            User.profile().where("occupation", "Developer").to_sql(),
            """SELECT * FROM "profiles_rel" WHERE "profiles_rel"."occupation" = 'Developer'""",
        )

    def test_can_access_relationship(self):
        users = User.where_in("id", [1, 3]).get()
        for user in users:
            self.assertIsInstance(user.profile, Profile)

    def test_can_access_has_many_relationship(self):
        user = User.where("id", 2).first()
        self.assertEqual(len(user.articles), 1)

    def test_can_access_relationship_multiple_times(self):
        user = User.where("id", 1).first()
        self.assertEqual(len(user.articles), 1)
        self.assertEqual(len(user.articles), 1)

    # def test_can_access_relationship_date(self):
    #     user = User.with_("articles_rel").where("id", 1).first()
    #     for article in user.articles:
    #         print(article.logo.published_date.is_past())
    #

    # def test_loading(self):
    #     users = User.with_("articles_rel").get()
    #     for user in users:
    #         user

    def test_relationship_has_one_sql(self):
        sql = 'SELECT * FROM "profiles_rel"'
        self.assertEqual(User.profile().to_sql(), sql)

    def test_loading_with_nested_with(self):
        users = User.with_("articles_rel", "articles.logo").get()
        for user in users:
            for article in user.articles:
                self.assertIsNotNone(article.logo)

    def test_casting(self):
        users = User.with_("articles_rel").where("is_admin", True).get()
        for user in users:
            self.assertIsInstance(user.is_admin, bool)

    # def test_setting(self):
    #     users = User.with_("articles_rel").where("is_admin", True).get()
    #     for user in users:
    #         user.name = "Joe"
    #         user.is_admin = 1
    #         user.save()
    #
    def test_related(self):
        user = User.first()
        related_query = user.related("profile").where("active", 1).to_sql()
        self.assertEqual(
            related_query,
            """SELECT * FROM "profiles_rel" WHERE "profiles_rel"."user_id" = '1' AND "profiles_rel"."active" = '1'""",
        )

    def test_associate_records(self):
        user = User.first()
        article_count = user.articles.count()
        # TODO: fix HasMany Relationship
        # articles = [Article.hydrate({"name": "associate records"})]
        # user.save_many("articles_rel", articles)
        # self.assertEqual(user.articles.count(), article_count+1)

    # def test_belongs_to_many(self):
    #     store = Store.hydrate({"id": 2, "name": "Walmart"})
    #     self.assertEqual(store.products.count(), 3)
    #     self.assertEqual(store.products.serialize()[0]["id"], 4)
    #     self.assertEqual(store.products.serialize()[0]["name"], "Handgun")
    #     self.assertEqual(
    #         store.products.serialize()[0]["updated_at"], "2020-01-01T00:00:00+00:00"
    #     )
    #     self.assertEqual(
    #         store.products.serialize()[0]["created_at"], "2020-01-01T00:00:00+00:00"
    #     )

    def test_belongs_to_eager_many(self):
        # store = Store.({"id": 2, "name": "Walmart"})
        store = Store.with_("products").first()
        self.assertEqual(store.products.count(), 3)
