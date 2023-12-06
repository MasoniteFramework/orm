import inspect
import unittest

from tests.integrations.config.database import DATABASES
from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar
from src.masoniteorm.relationships import belongs_to, belongs_to_many
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms.SQLitePlatform import SQLitePlatform
from tests.utils import MockConnectionFactory


class User(Model):
    __connection__ = "dev"
    __timestamps__ = False
    __dry__ = True


class UserForced(Model):
    __connection__ = "dev"
    __table__ = "users"
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


class BaseTestQueryRelationships(unittest.TestCase):
    maxDiff = None

    def test_update_specific_record(self):
        user = User.first()
        sql = user.update({"name": "joe"}).to_sql()

        self.assertEqual(
            sql,
            """UPDATE "users" SET "name" = 'joe' WHERE "id" = '{}'""".format(user.id),
        )

    def test_update_all_records(self):
        sql = User.update({"name": "joe"}).to_sql()

        self.assertEqual(sql, """UPDATE "users" SET "name" = 'joe'""")

    def test_can_find_list(self):
        sql = User.find(1, query=True)

        self.assertEqual(sql, """SELECT * FROM "users" WHERE "users"."id" = '1'""")

        sql = User.find([1, 2, 3], query=True)

        self.assertEqual(
            sql, """SELECT * FROM "users" WHERE "users"."id" IN ('1','2','3')"""
        )

    def test_find_or_if_record_not_found(self):
        # Insane record number so record cannot be found
        record_id = 1_000_000_000_000_000

        result = User.find_or(record_id, lambda: "Record not found.")
        self.assertEqual(result, "Record not found.")

    def test_find_or_if_record_found(self):
        record_id = 1
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
            SelectPass.all(["username"], query=True),
            'SELECT "select_passes"."username" FROM "select_passes"',
        )

    def test_update_only_changed_attributes(self):
        user = User.first()
        sql = user.update({"name": user.name, "username": "new"}).to_sql()
        # unchanged name attribute is not updated
        self.assertEqual(
            sql,
            """UPDATE "users" SET "username" = 'new' WHERE "id" = '{}'""".format(
                user.id
            ),
        )

    def test_can_force_update_on_method(self):
        user = User.first()
        sql = user.update({"name": user.name, "username": "new"}, force=True).to_sql()
        self.assertEqual(
            sql,
            """UPDATE "users" SET "name" = 'bill', "username" = 'new' WHERE "id" = '{}'""".format(
                user.id
            ),
        )

    def test_can_force_update_on_model(self):
        user = UserForced.first()
        sql = user.update({"name": user.name, "username": "new"}).to_sql()
        self.assertEqual(
            sql,
            """UPDATE "users" SET "name" = 'bill', "username" = 'new' WHERE "id" = '{}'""".format(
                user.id
            ),
        )

    def test_force_update(self):
        user = User.first()
        sql = user.force_update({"name": user.name, "username": "new"}).to_sql()
        self.assertEqual(
            sql,
            """UPDATE "users" SET "name" = 'bill', "username" = 'new' WHERE "id" = '{}'""".format(
                user.id
            ),
        )

    def test_update_is_not_done_when_no_changes(self):
        user = User.first()
        sql = user.update({"name": user.name}).to_sql()
        self.assertNotIn("UPDATE", sql)

    def test_should_collect_correct_amount_data_using_between(self):
        class ModelUser(Model):
            __connection__ = "dev"
            __table__ = "users"

        count = User.between("age", 1, 2).get().count()
        self.assertEqual(count, 2)

    def test_should_collect_correct_amount_data_using_not_between(self):
        class ModelUser(Model):
            __connection__ = "dev"
            __table__ = "users"

        count = User.where_not_null("id").not_between("age", 1, 2).get().count()
        self.assertEqual(count, 0)

    def test_get_columns(self):
        columns = User.get_columns()
        self.assertEqual(
            columns,
            [
                "id",
                "name",
                "email",
                "password",
                "remember_token",
                "created_at",
                "is_admin",
                "age",
                "boo",
                "tool1",
                "tool2",
                "active",
                "updated_at",
                "profile_id",
                "name5",
                "name6",
                "age6",
                "age7",
                "age8",
                "age10",
            ],
        )

    def test_should_return_relation_applying_hidden_attributes(self):
        schema = Schema(
            connection_details=DATABASES, connection="dev", platform=SQLitePlatform
        ).on("dev")

        tables = ["users_hidden", "group_user", "groups"]

        for table in tables:
            schema.drop_table_if_exists(table)

        with schema.create("users_hidden") as blueprint:
            blueprint.increments("id")
            blueprint.string("name")
            blueprint.integer("token")
            blueprint.string("password")
            blueprint.timestamps()

        with schema.create("groups") as blueprint:
            blueprint.increments("id")
            blueprint.string("name")
            blueprint.timestamps()

        with schema.create("group_user") as blueprint:
            blueprint.increments("id")

            blueprint.unsigned_integer("group_id")
            blueprint.unsigned_integer("user_id")

            blueprint.foreign("group_id").references("id").on("groups")
            blueprint.foreign("user_id").references("id").on("users_hidden")
            blueprint.timestamps()

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

        for table in tables:
            schema.truncate(table)
