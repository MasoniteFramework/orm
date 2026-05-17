import os
import unittest
from pathlib import Path

import pytest

from src.masoniteorm.config import load_config
from src.masoniteorm.connections import ConnectionResolver
from src.masoniteorm.exceptions import (
    HTTP404,
    ConfigurationNotFound,
    ModelNotFound,
    QueryException,
)
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar
from tests.utils import MockConnectionFactory


class UserMock(Model):
    __connection__ = "dev"
    __table__ = "users"


class SQLiteQueryBuilderTest(unittest.TestCase):
    """Tests for the QueryBuilder using the SQLite grammar.

    Each test builds a query and asserts the expected SQL inline.
    """

    maxDiff = None

    def get_builder(self, table="users"):
        connection = MockConnectionFactory().make("sqlite")
        return QueryBuilder(
            grammar=SQLiteGrammar,
            connection_class=connection,
            table=table,
            dry=True,
        )

    # ------------------------------------------------------------------
    # Connection / config tests
    # ------------------------------------------------------------------

    def test_standalone_connection_details(self):
        current_path = os.environ.pop("DB_CONFIG_PATH", None)
        with pytest.raises(ConfigurationNotFound):
            load_config()

        custom_details = {
            "default": "test",
            "test": {
                "driver": "sqlite",
                "database": "config_test.sqlite3",
            },
        }
        resolver = ConnectionResolver(connection_details=custom_details)
        connection = resolver.connection_factory.make("sqlite")
        builder = QueryBuilder(
            connection_details=custom_details, connection_class=connection
        )
        with pytest.raises(QueryException) as query_exc:
            builder.table("tests").all()
        self.assertIn("'no such table: tests'", str(query_exc))
        (Path().cwd() / "config_test.sqlite3").unlink()
        os.environ["DB_CONFIG_PATH"] = current_path

    # ------------------------------------------------------------------
    # Aggregates
    # ------------------------------------------------------------------

    def test_sum(self):
        builder = self.get_builder()
        builder.sum("age")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT SUM("users"."age") AS age FROM "users"'
        self.assertEqual(query_sql, expected_sql)

    def test_sum_aggregate(self):
        builder = self.get_builder()
        builder.aggregate("SUM", "age")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT SUM("users"."age") AS age FROM "users"'
        self.assertEqual(query_sql, expected_sql)

    def test_sum_aggregate_with_alias(self):
        builder = self.get_builder()
        builder.aggregate("SUM", "age", alias="number")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT SUM("users"."age") AS number FROM "users"'
        self.assertEqual(query_sql, expected_sql)

    def test_sum_aggregate_with_alias_in_column_name(self):
        builder = self.get_builder()
        builder.sum("age as number")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT SUM("users"."age") AS number FROM "users"'
        self.assertEqual(query_sql, expected_sql)

    def test_max(self):
        builder = self.get_builder()
        builder.max("age")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT MAX("users"."age") AS age FROM "users"'
        self.assertEqual(query_sql, expected_sql)

    def test_min(self):
        builder = self.get_builder()
        builder.min("age")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT MIN("users"."age") AS age FROM "users"'
        self.assertEqual(query_sql, expected_sql)

    def test_avg(self):
        builder = self.get_builder()
        builder.avg("age")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT AVG("users"."age") AS age FROM "users"'
        self.assertEqual(query_sql, expected_sql)

    def test_count(self):
        builder = self.get_builder()
        builder.count("id")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT COUNT("users"."id") AS id FROM "users"'
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # Fetch operations
    # ------------------------------------------------------------------

    def test_all(self):
        builder = self.get_builder()
        builder.all()
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users"'
        self.assertEqual(query_sql, expected_sql)

    def test_get(self):
        builder = self.get_builder()
        builder.get()
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users"'
        self.assertEqual(query_sql, expected_sql)

    def test_first(self):
        builder = self.get_builder().first(query=True)
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" LIMIT 1'
        self.assertEqual(query_sql, expected_sql)

    def test_last(self):
        last_id = UserMock.last("id").id
        first_desc_id = UserMock.order_by("id", "DESC").first().id
        self.assertEqual(last_id, first_desc_id)

    def test_last_with_default_primary_key(self):
        last_id = UserMock.last().id
        first_desc_id = UserMock.order_by("id", "DESC").first().id
        self.assertEqual(last_id, first_desc_id)

    def test_first_or_fail_exception(self):
        with self.assertRaises(ModelNotFound):
            self.get_builder().where("name", "=", "Marlysson").first_or_fail()

    def test_find_or_fail_exception(self):
        with self.assertRaises(ModelNotFound):
            UserMock.find_or_fail(1000)

    def test_find_or_404_exception(self):
        with self.assertRaises(HTTP404):
            UserMock.find_or_404(1000)

    # ------------------------------------------------------------------
    # SELECT columns
    # ------------------------------------------------------------------

    def test_select(self):
        builder = self.get_builder()
        builder.select("name", "email")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT "users"."name", "users"."email" FROM "users"'
        self.assertEqual(query_sql, expected_sql)

    def test_select_multiple(self):
        builder = self.get_builder()
        builder.select("name", "email")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT "users"."name", "users"."email" FROM "users"'
        self.assertEqual(query_sql, expected_sql)

    def test_add_select(self):
        builder = self.get_builder()
        builder.select("name").add_select(
            "phone_count", lambda q: q.count("*").table("phones")
        ).add_select("salary", lambda q: q.count("*").table("salary"))
        query_sql = builder.to_sql()
        expected_sql = (
            'SELECT "users"."name",'
            ' (SELECT COUNT(*) AS m_count_reserved FROM "phones") AS phone_count,'
            ' (SELECT COUNT(*) AS m_count_reserved FROM "salary") AS salary'
            ' FROM "users"'
        )
        self.assertEqual(query_sql, expected_sql)

    def test_add_select_no_table(self):
        builder = self.get_builder(table=None)
        builder.add_select(
            "other_test",
            lambda q: q.max("updated_at").table("different_table"),
        ).add_select(
            "some_alias", lambda q: q.max("updated_at").table("another_table")
        )
        query_sql = builder.to_sql()
        expected_sql = (
            "SELECT "
            '(SELECT MAX("different_table"."updated_at") AS updated_at FROM "different_table") AS other_test, '
            '(SELECT MAX("another_table"."updated_at") AS updated_at FROM "another_table") AS some_alias'
        )
        self.assertEqual(query_sql, expected_sql)

    def test_add_select_with_raw(self):
        builder = self.get_builder(table=None)
        builder.select_raw("max(updated_at) as test").from_(
            "some_table"
        ).add_select(
            "other_test",
            lambda query: query.max("updated_at")
            .from_("different_table")
            .where("some_id", "=", "3"),
        )
        query_sql = builder.to_sql()
        expected_sql = (
            "SELECT max(updated_at) as test, "
            '(SELECT MAX("different_table"."updated_at") AS updated_at '
            'FROM "different_table" '
            'WHERE "different_table"."some_id" = \'3\') AS other_test '
            'FROM "some_table"'
        )
        self.assertEqual(query_sql, expected_sql)

    def test_select_raw(self):
        builder = self.get_builder()
        builder.select_raw("count(email) as email_count")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT count(email) as email_count FROM "users"'
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # WHERE
    # ------------------------------------------------------------------

    def test_where(self):
        builder = self.get_builder()
        builder.where("name", "Joe")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" WHERE "users"."name" = \'Joe\''
        self.assertEqual(query_sql, expected_sql)

    def test_where_dictionary(self):
        builder = self.get_builder()
        builder.where({"name": "Joe"})
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" WHERE "users"."name" = \'Joe\''
        self.assertEqual(query_sql, expected_sql)

    def test_where_exists(self):
        builder = self.get_builder()
        builder.where_exists("name")
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM \"users\" WHERE EXISTS 'name'"
        self.assertEqual(query_sql, expected_sql)

    def test_where_like(self):
        builder = self.get_builder()
        builder.where("age", "like", "%name%")
        query_sql = builder.to_sql()
        expected_sql = (
            'SELECT * FROM "users" WHERE "users"."age" LIKE \'%name%\''
        )
        self.assertEqual(query_sql, expected_sql)

    def test_where_not_like(self):
        builder = self.get_builder()
        builder.where("age", "not like", "%name%")
        query_sql = builder.to_sql()
        expected_sql = (
            'SELECT * FROM "users" WHERE "users"."age" NOT LIKE \'%name%\''
        )
        self.assertEqual(query_sql, expected_sql)

    def test_where_null(self):
        builder = self.get_builder()
        builder.where_null("name")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" WHERE "users"."name" IS NULL'
        self.assertEqual(query_sql, expected_sql)

    def test_where_not_null(self):
        builder = self.get_builder()
        builder.where_not_null("name")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" WHERE "users"."name" IS NOT NULL'
        self.assertEqual(query_sql, expected_sql)

    def test_where_not_in(self):
        builder = self.get_builder()
        builder.where_not_in("id", [1, 2, 3])
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM \"users\" WHERE \"users\".\"id\" NOT IN ('1','2','3')"
        self.assertEqual(query_sql, expected_sql)

    def test_where_in(self):
        builder = self.get_builder()
        builder.where_in("id", [1, 2, 3])
        query_sql = builder.to_sql()
        expected_sql = (
            "SELECT * FROM \"users\" WHERE \"users\".\"id\" IN ('1','2','3')"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_where_lt(self):
        builder = self.get_builder()
        builder.where("age", "<", "20")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" WHERE "users"."age" < \'20\''
        self.assertEqual(query_sql, expected_sql)

    def test_where_lte(self):
        builder = self.get_builder()
        builder.where("age", "<=", "20")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" WHERE "users"."age" <= \'20\''
        self.assertEqual(query_sql, expected_sql)

    def test_where_gt(self):
        builder = self.get_builder()
        builder.where("age", ">", "20")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" WHERE "users"."age" > \'20\''
        self.assertEqual(query_sql, expected_sql)

    def test_where_gte(self):
        builder = self.get_builder()
        builder.where("age", ">=", "20")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" WHERE "users"."age" >= \'20\''
        self.assertEqual(query_sql, expected_sql)

    def test_where_ne(self):
        builder = self.get_builder()
        builder.where("age", "!=", "20")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" WHERE "users"."age" != \'20\''
        self.assertEqual(query_sql, expected_sql)

    def test_or_where(self):
        builder = self.get_builder()
        builder.where("age", "20").or_where("age", "<", 20)
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" WHERE "users"."age" = \'20\' OR "users"."age" < \'20\''
        self.assertEqual(query_sql, expected_sql)

    def test_where_column(self):
        builder = self.get_builder()
        builder.where_column("name", "username")
        query_sql = builder.to_sql()
        expected_sql = (
            'SELECT * FROM "users" WHERE "users"."name" = "users"."username"'
        )
        self.assertEqual(query_sql, expected_sql)

    def test_between(self):
        builder = self.get_builder()
        builder.between("id", 2, 5)
        query_sql = builder.to_sql()
        expected_sql = (
            'SELECT * FROM "users" WHERE "users"."id" BETWEEN \'2\' AND \'5\''
        )
        self.assertEqual(query_sql, expected_sql)

    def test_between_persisted(self):
        builder = QueryBuilder().table("users").on("dev")
        users = builder.between("age", 21, 25).count()
        self.assertEqual(users, 2)

    def test_not_between(self):
        builder = self.get_builder()
        builder.not_between("id", 2, 5)
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" WHERE "users"."id" NOT BETWEEN \'2\' AND \'5\''
        self.assertEqual(query_sql, expected_sql)

    def test_not_between_persisted(self):
        builder = QueryBuilder().table("users").on("dev")
        users = builder.where_not_null("id").not_between("age", 1, 10).count()
        self.assertEqual(users, 2)

    def test_having(self):
        builder = self.get_builder(table="payments")
        builder.select("user_id").avg("salary").group_by("user_id").having(
            "salary", ">=", "1000"
        )
        query_sql = builder.to_sql()
        expected_sql = (
            'SELECT "payments"."user_id", AVG("payments"."salary") AS salary'
            ' FROM "payments" GROUP BY "payments"."user_id" HAVING "payments"."salary" >= \'1000\''
        )
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # LIMIT / OFFSET
    # ------------------------------------------------------------------

    def test_limit(self):
        builder = self.get_builder()
        builder.limit(5)
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" LIMIT 5'
        self.assertEqual(query_sql, expected_sql)

    def test_offset(self):
        builder = self.get_builder()
        builder.offset(5)
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" LIMIT -1 OFFSET 5'
        self.assertEqual(query_sql, expected_sql)

    def test_offset_with_limit(self):
        builder = self.get_builder()
        builder.limit(2).offset(5)
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" LIMIT 2 OFFSET 5'
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # ORDER BY / GROUP BY
    # ------------------------------------------------------------------

    def test_order_by_asc(self):
        builder = self.get_builder()
        builder.order_by("email", "asc")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" ORDER BY "email" ASC'
        self.assertEqual(query_sql, expected_sql)

    def test_order_by_desc(self):
        builder = self.get_builder()
        builder.order_by("email", "desc")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" ORDER BY "email" DESC'
        self.assertEqual(query_sql, expected_sql)

    def test_order_by_multiple(self):
        builder = self.get_builder()
        builder.order_by("email, name, active")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" ORDER BY "email" ASC, "name" ASC, "active" ASC'
        self.assertEqual(query_sql, expected_sql)

    def test_order_by_raw(self):
        builder = self.get_builder()
        builder.order_by_raw("col asc")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" ORDER BY col asc'
        self.assertEqual(query_sql, expected_sql)

    def test_order_by_reference_direction(self):
        builder = self.get_builder()
        builder.order_by("email, name desc")
        query_sql = builder.to_sql()
        expected_sql = (
            'SELECT * FROM "users" ORDER BY "email" ASC, "name" DESC'
        )
        self.assertEqual(query_sql, expected_sql)

    def test_latest(self):
        builder = self.get_builder()
        builder.latest("email")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" ORDER BY "email" DESC'
        self.assertEqual(query_sql, expected_sql)

    def test_oldest(self):
        builder = self.get_builder()
        builder.oldest("email")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" ORDER BY "email" ASC'
        self.assertEqual(query_sql, expected_sql)

    def test_group_by(self):
        builder = self.get_builder(table="payments")
        builder.select("user_id").min("salary").group_by("user_id")
        query_sql = builder.to_sql()
        expected_sql = (
            'SELECT "payments"."user_id", MIN("payments"."salary") AS salary'
            ' FROM "payments" GROUP BY "payments"."user_id"'
        )
        self.assertEqual(query_sql, expected_sql)

    def test_group_by_multiple(self):
        builder = self.get_builder(table="payments")
        builder.select("user_id").min("salary").group_by("user_id").group_by(
            "salary"
        )
        query_sql = builder.to_sql()
        expected_sql = (
            'SELECT "payments"."user_id", MIN("payments"."salary") AS salary'
            ' FROM "payments" GROUP BY "payments"."user_id", "payments"."salary"'
        )
        self.assertEqual(query_sql, expected_sql)

    def test_group_by_multiple_in_same_group_by(self):
        builder = self.get_builder(table="payments")
        builder.select("user_id").min("salary").group_by("user_id, salary")
        query_sql = builder.to_sql()
        expected_sql = (
            'SELECT "payments"."user_id", MIN("payments"."salary") AS salary'
            ' FROM "payments" GROUP BY "payments"."user_id", "payments"."salary"'
        )
        self.assertEqual(query_sql, expected_sql)

    def test_group_by_raw(self):
        builder = self.get_builder(table="payments")
        builder.select("user_id").min("salary").group_by_raw("count(*)")
        query_sql = builder.to_sql()
        expected_sql = (
            'SELECT "payments"."user_id", MIN("payments"."salary") AS salary'
            ' FROM "payments" GROUP BY count(*)'
        )
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # JOINs
    # ------------------------------------------------------------------

    def test_join(self):
        builder = self.get_builder()
        builder.join("profiles", "users.id", "=", "profiles.user_id")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" INNER JOIN "profiles" ON "users"."id" = "profiles"."user_id"'
        self.assertEqual(query_sql, expected_sql)

    def test_left_join(self):
        builder = self.get_builder()
        builder.left_join("profiles", "users.id", "=", "profiles.user_id")
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" LEFT JOIN "profiles" ON "users"."id" = "profiles"."user_id"'
        self.assertEqual(query_sql, expected_sql)

    def test_right_join(self):
        builder = self.get_builder()
        builder.right_join("profiles", "users.id", "=", "profiles.user_id")
        # SQLite has no RIGHT JOIN; it is emitted as LEFT JOIN
        query_sql = builder.to_sql()
        expected_sql = 'SELECT * FROM "users" LEFT JOIN "profiles" ON "users"."id" = "profiles"."user_id"'
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # DML
    # ------------------------------------------------------------------

    def test_create(self):
        builder = self.get_builder()
        builder.create(
            {"name": "Corentin All", "email": "corentin@yopmail.com"},
            query=True,
        )
        query_sql = builder.to_sql()
        expected_sql = 'INSERT INTO "users" ("name", "email") VALUES (\'Corentin All\', \'corentin@yopmail.com\')'
        self.assertEqual(query_sql, expected_sql)

    def test_delete(self):
        builder = self.get_builder()
        builder.delete("name", "Joe", query=True)
        query_sql = builder.to_sql()
        expected_sql = 'DELETE FROM "users" WHERE "name" = \'Joe\''
        self.assertEqual(query_sql, expected_sql)

    def test_update(self):
        builder = self.get_builder().update(
            {"name": "Joe", "email": "joe@yopmail.com"}, dry=True
        )
        query_sql = builder.to_sql()
        expected_sql = 'UPDATE "users" SET "name" = \'Joe\', "email" = \'joe@yopmail.com\''
        self.assertEqual(query_sql, expected_sql)

    def test_increment(self):
        builder = self.get_builder().increment("age", 1, dry=True)
        query_sql = builder.to_sql()
        expected_sql = 'UPDATE "users" SET "age" = "age" + \'1\''
        self.assertEqual(query_sql, expected_sql)

    def test_decrement(self):
        builder = self.get_builder().decrement("age", 1, dry=True)
        query_sql = builder.to_sql()
        expected_sql = 'UPDATE "users" SET "age" = "age" - \'1\''
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # TRUNCATE
    # ------------------------------------------------------------------

    def test_truncate(self):
        builder = self.get_builder()
        query_sql = builder.truncate(dry=True)
        expected_sql = 'DELETE FROM "users"'
        self.assertEqual(query_sql, expected_sql)

    def test_truncate_without_foreign_keys(self):
        builder = self.get_builder()
        query_sql = builder.truncate(foreign_keys=True)
        expected_sql = [
            "PRAGMA foreign_keys = OFF",
            'DELETE FROM "users"',
            "PRAGMA foreign_keys = ON",
        ]
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # Conditional / misc
    # ------------------------------------------------------------------

    def test_when_condition_true(self):
        builder = self.get_builder()
        query_sql = builder.when(
            19 > 18, lambda q: q.where("age_restricted", 1)
        ).to_sql()
        expected_sql = (
            'SELECT * FROM "users" WHERE "users"."age_restricted" = \'1\''
        )
        self.assertEqual(query_sql, expected_sql)

    def test_when_condition_false(self):
        builder = self.get_builder()
        query_sql = builder.when(
            17 > 18, lambda q: q.where("age_restricted", 1)
        ).to_sql()
        expected_sql = 'SELECT * FROM "users"'
        self.assertEqual(query_sql, expected_sql)

    def test_builder_alone(self):
        self.assertTrue(
            QueryBuilder(
                connection_details={
                    "default": "sqlite",
                    "sqlite": {
                        "driver": "sqlite",
                        "database": "orm.sqlite3",
                        "prefix": "",
                    },
                }
            ).table("users")
        )

    def test_can_call_with_schema(self):
        builder = self.get_builder()
        query_sql = (
            builder.table("information_schema.columns")
            .select("table_name")
            .where("table_name", "users")
            .to_sql()
        )
        expected_sql = (
            'SELECT "information_schema"."columns"."table_name" FROM "information_schema"."columns"'
            ' WHERE "information_schema"."columns"."table_name" = \'users\''
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_call_with_raw(self):
        builder = self.get_builder()
        query_sql = builder.on("dev").statement("select * from users")
        self.assertTrue(query_sql)
