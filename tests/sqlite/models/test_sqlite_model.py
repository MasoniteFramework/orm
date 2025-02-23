import unittest

from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.relationships import belongs_to_many
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms.SQLitePlatform import SQLitePlatform
from tests.integrations.config.database import DATABASES


class User(Model):
    __connection__ = "dev"
    __timestamps__ = False


class AltUser(Model):
    __connection__ = "dev"
    __timestamps__ = False
    __table__ = "alt_users"


class UserForced(Model):
    __connection__ = "dev"
    __table__ = "forced_users"
    __timestamps__ = False
    __dry__ = True
    __force_update__ = True


class Select(Model):
    __connection__ = "dev"
    __selects__ = ["username", "rememember_token as token"]
    __dry__ = True


class SelectPass(Model):
    __connection__ = "dev"
    __dry__ = True


class UserHydrateHidden(Model):
    __connection__ = "dev"
    __table__ = "users_hidden"
    __hidden__ = ["token", "password"]


class Group(Model):
    __connection__ = "dev"
    __table__ = "groups"
    __fillable = ["name"]
    __with__ = ["team"]

    @belongs_to_many("group_id", "user_id", "id", "id", table="group_user")
    def team(self):
        return UserHydrateHidden


class SqliteTestModel(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.dev_builder = QueryBuilder().on("dev")
        cls.connection = ConnectionFactory().make("sqlite")
        cls.schema = Schema(
            # grammar=SQLiteGrammar,
            connection="dev",
            connection_class=cls.connection,
            connection_details=DATABASES,
            platform=SQLitePlatform,
        ).on("dev")

        cls.schema.drop_table_if_exists("users")
        with cls.schema.create("users") as table:
            table.integer("id").primary()
            table.string("name")
            table.string("email")
            table.integer("age")

        cls.schema.drop_table_if_exists("forced_users")
        with cls.schema.create("forced_users") as table:
            table.integer("id").primary()
            table.string("name")
            table.string("email")
            table.integer("age")

        cls.schema.drop_table_if_exists("alt_users")
        with cls.schema.create("alt_users") as table:
            table.integer("id").primary()
            table.string("name")
            table.string("email")
            table.integer("age")

        cls.schema.drop_table_if_exists("users_hidden")
        with cls.schema.create("users_hidden") as blueprint:
            blueprint.increments("id")
            blueprint.string("name")
            blueprint.integer("token")
            blueprint.string("password")
            blueprint.timestamps()

        cls.schema.drop_table_if_exists("groups")
        with cls.schema.create("groups") as blueprint:
            blueprint.increments("id")
            blueprint.string("name")
            blueprint.timestamps()

        cls.schema.drop_table_if_exists("group_user")
        with cls.schema.create("group_user") as blueprint:
            blueprint.increments("id")
            blueprint.unsigned_integer("group_id")
            blueprint.unsigned_integer("user_id")
            blueprint.foreign("group_id").references("id").on("groups")
            blueprint.foreign("user_id").references("id").on("users_hidden")
            blueprint.timestamps()

        cls.dev_builder.table("users").bulk_create(
            [
                {"name": "Steve", "email": "steve@masonite.com", "age": 3},
                {"name": "Joe", "email": "joe@masonite.com", "age": 2},
                {"name": "Bob", "email": "bob@masonite.com", "age": 1},
            ]
        )
        cls.dev_builder.table("forced_users").bulk_create(
            [
                {"name": "Steve", "email": "steve@masonite.com", "age": 3},
                {"name": "Joe", "email": "joe@masonite.com", "age": 2},
                {"name": "Bob", "email": "bob@masonite.com", "age": 1},
            ]
        )

    @classmethod
    def tearDownClass(cls):
        cls.schema.drop_table_if_exists("users")
        cls.schema.drop_table_if_exists("forced_users")
        cls.schema.drop_table_if_exists("users_hidden")
        cls.schema.drop_table_if_exists("groups")
        cls.schema.drop_table_if_exists("group_user")

    def test_update_specific_record(self):
        user = User.find(1)
        user.update({"name": "joe"})
        # get the user again to make sure
        check_user = User.find(1)
        self.assertEqual(check_user.name, "joe")

    def test_update_all_records(self):
        User.update({"name": "joe"})
        all_users = User.all()
        for user in all_users:
            self.assertEqual(user.name, "joe")

    def test_can_find_list(self):
        sql = User.find(1, query=True).to_sql()
        self.assertEqual(sql, """SELECT * FROM "users" WHERE "users"."id" = '1'""")

        sql = User.find([1, 2, 3], query=True).to_sql()
        self.assertEqual(
            sql, """SELECT * FROM "users" WHERE "users"."id" IN ('1','2','3')"""
        )

    def test_find_or_if_record_not_found(self):
        # Insane record number so record cannot be found
        record_id = 1_000_000_000_000_000
        result = User.find_or(record_id, lambda: "Record not found.")
        self.assertEqual(result, "Record not found.")

    def test_find_or_if_record_found(self):
        record_id = 2
        result_id = User.find_or(record_id, lambda: "Record not found.").id
        self.assertEqual(result_id, record_id)

    def test_can_set_and_retreive_attribute(self):
        user = User.hydrate({"id": 1, "name": "joe", "customer_id": 1})
        user.customer_id = "CUST1"
        self.assertEqual(user.customer_id, "CUST1")

    def test_model_can_use_selects(self):
        self.assertEqual(
            Select.to_sql(),
            'SELECT "selects"."username", "selects"."rememember_token" AS token FROM "selects"',
        )

    def test_model_can_use_selects_from_methods(self):

        self.assertEqual(
            SelectPass.all(["username"], query=True).to_sql(),
            'SELECT "select_passes"."username" FROM "select_passes"',
        )

    def test_update_only_changed_attributes(self):
        user = User.first()
        sql = user.update(
            {"name": user.name, "email": "different@domain.com"}, dry=True
        ).to_sql()
        # TODO: fix dry .update returns select query
        # unchanged name attribute is not updated
        # self.assertEqual(
        #     sql,
        #     """UPDATE "users" SET "email" = 'different@domain.com' WHERE "id" = '{}'""".format(
        #         user.id
        #     ),
        # )

    def test_can_force_update_on_method(self):
        user = User.first()
        # Todo: fix Model not passing keyword args to querybuilder for update()
        # sql = user.update({"name": user.name, "email": "new@domain.com"}, force=True).to_sql()
        # self.assertEqual(
        #     sql,
        #     """UPDATE "users" SET "name" = 'bill', "username" = 'new' WHERE "id" = '{}'""".format(
        #         user.id
        #     ),
        # )

    def test_can_force_update_on_model(self):
        user = UserForced.first()
        sql = user.update({"name": user.name, "email": "new@domain.com"}).to_sql()

        self.assertEqual(
            sql,
            """UPDATE "forced_users" SET "name" = 'Steve', "email" = 'new@domain.com' WHERE "id" = '{}'""".format(
                user.id
            ),
        )

    def test_force_update(self):
        user = User.first()
        sql = user.force_update(
            {"name": user.name, "email": "new@domain.com"}, dry=True
        ).to_sql()

        self.assertEqual(
            sql,
            """UPDATE "users" SET "name" = 'Steve', "email" = 'new@domain.com' WHERE "id" = '{}'""".format(
                user.id
            ),
        )

    def test_update_is_not_done_when_no_changes(self):
        user = User().first()
        sql = user.update({"name": user.name}).to_sql()
        self.assertNotIn("UPDATE", sql)

    def test_should_collect_correct_amount_data_using_between(self):
        count = User.between("age", 1, 2).get().count()
        self.assertEqual(count, 2)

    def test_should_collect_correct_amount_data_using_not_between(self):
        count = User.where_not_null("id").not_between("age", 1, 2).get().count()
        self.assertEqual(count, 1)

    def test_get_columns(self):
        self.schema.drop_table("alt_users")
        with self.schema.create("alt_users") as setup:
            setup.increments("id")
            setup.string("name")
            setup.enum("gender", ["male", "female"])
            setup.string("email").unique()
            setup.string("password")
            setup.string("option").default("ADMIN")
            setup.integer("admin").default(0)
            setup.string("remember_token").nullable()
            setup.timestamp("verified_at").nullable()
            setup.unique(["email", "name"])
            setup.timestamps()

        # add a single record so we can hydrate the model
        AltUser.create(
            {
                "name": "Steve",
                "gender": "male",
                "email": "test@domain.com",
                "password": "secret",
            }
        )

        columns = AltUser.first().get_columns()
        self.assertEqual(
            columns,
            [
                "id",
                "name",
                "gender",
                "email",
                "password",
                "option",
                "admin",
                "remember_token",
                "verified_at",
                "created_at",
                "updated_at",
            ],
        )

    def test_should_return_relation_applying_hidden_attributes(self):
        UserHydrateHidden.create(
            name="Name", password="pass_value", token="token_value"
        )

        Group.create(name="Group")

        user = UserHydrateHidden.first()
        group = Group.first()

        group.attach_related("team", user)

        serialized = Group.first().serialize()

        self.assertIn("team", serialized)
        self.assertTrue("team", serialized)

        relation_serialized = serialized.get("team")

        self.assertNotIn("password", relation_serialized)
        self.assertNotIn("token", relation_serialized)
