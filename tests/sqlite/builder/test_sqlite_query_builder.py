import unittest

from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.exceptions import HTTP404, ModelNotFound
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import SQLiteGrammar
from src.masoniteorm.schema import Schema
from src.masoniteorm.schema.platforms import SQLitePlatform
from tests.integrations.config.database import DATABASES


class SqliteTestQueryBuilder(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.dev_builder = QueryBuilder().on("dev")
        cls.connection = ConnectionFactory().make("sqlite")
        cls.schema = Schema(
            connection="dev",
            connection_details=DATABASES,
            platform=SQLitePlatform,
        ).on("dev")

        cls.schema.drop_table_if_exists("users_query")
        with cls.schema.create("users_query") as table:
            table.integer("id").primary()
            table.string("name", nullable=True)
            table.string("email")
            table.string("age")

    def setUp(self):
        self.dev_builder.table("users_query").bulk_create(
            [
                {"name": "Steve", "age": 13, "email": "steve@domain.com"},
                {"name": "Joe", "age": 23, "email": "joe@masonite.com"},
                {"name": "Bob", "age": 13, "email": "bob@domain.com"},
            ]
        )

    def tearDown(self):
        self.schema.truncate("users_query")

    @classmethod
    def tearDownClass(cls):
        cls.schema.drop_table_if_exists("users_query")

    def get_builder(self, table="users_query"):
        return QueryBuilder(
            grammar=SQLiteGrammar,
            connection_class=self.connection,
            connection="dev",
            table=table,
            dry=True,
        ).new()

    def test_sum(self):
        builder = self.get_builder()
        builder.sum("age")
        sql = '''SELECT SUM("users_query"."age") AS age FROM "users_query"'''
        self.assertEqual(builder.to_sql(), sql)
        self.assertEqual(builder.first()["age"], 49)

    def test_sum_aggregate(self):
        builder = self.get_builder()
        builder.aggregate("SUM", "age")
        sql = '''SELECT SUM("users_query"."age") AS age FROM "users_query"'''
        self.assertEqual(builder.to_sql(), sql)
        self.assertEqual(builder.first()["age"], 49)

    def test_sum_aggregate_with_alias(self):
        builder = self.get_builder()
        builder.aggregate("SUM", "age", alias="number")
        sql = '''SELECT SUM("users_query"."age") AS number FROM "users_query"'''
        self.assertEqual(builder.to_sql(), sql)
        self.assertEqual(builder.first()["number"], 49)

    def test_sum_aggregate_with_alias_in_column_name(self):
        builder = self.get_builder()
        builder.sum("age as number")
        sql = '''SELECT SUM("users_query"."age") AS number FROM "users_query"'''
        self.assertEqual(builder.to_sql(), sql)
        self.assertEqual(builder.first()["number"], 49)

    def test_where_like(self):
        builder = self.get_builder()
        builder.where("email", "like", "%domain%")
        sql = """SELECT * FROM "users_query" WHERE "users_query"."email" LIKE '%domain%\'"""
        self.assertEqual(builder.to_sql(), sql)
        self.assertEqual(builder.get().count(), 2)

    def test_where_not_like(self):
        builder = self.get_builder()
        builder.where("age", "not like", "%name%")
        sql = """SELECT * FROM "users_query" WHERE "users_query"."age" NOT LIKE '%name%\'"""
        self.assertEqual(builder.to_sql(), sql)

    def test_max(self):
        builder = self.get_builder()
        builder.max("age")
        sql = '''SELECT MAX("users_query"."age") AS age FROM "users_query"'''
        self.assertEqual(builder.to_sql(), sql)
        self.assertEqual(builder.first()["age"], "23")

    def test_min(self):
        builder = self.get_builder()
        builder.min("age")
        sql = '''SELECT MIN("users_query"."age") AS age FROM "users_query"'''
        self.assertEqual(builder.to_sql(), sql)
        self.assertEqual(builder.first()["age"], "13")

    def test_avg(self):
        builder = self.get_builder()
        builder.avg("age")
        sql = '''SELECT AVG("users_query"."age") AS age FROM "users_query"'''
        self.assertEqual(builder.to_sql(), sql)
        self.assertEqual(round(builder.first()["age"], 2), 16.33)

    def test_all(self):
        builder = self.get_builder()
        builder.get()
        sql = '''SELECT * FROM "users_query"'''
        self.assertEqual(builder.to_sql(), sql)
        self.assertEqual(builder.get().count(), 3)

    def test_get(self):
        builder = self.get_builder()
        builder.get()
        sql = '''SELECT * FROM "users_query"'''
        self.assertEqual(builder.to_sql(), sql)
        self.assertEqual(builder.get().count(), 3)

    def test_first(self):
        builder = self.get_builder()
        builder.order_by("name").first(query=True)
        sql = """SELECT * FROM "users_query" ORDER BY "name" ASC LIMIT 1"""
        self.assertEqual(builder.to_sql(), sql)

        # get a new instance of the builder
        # required after instance was used for other task
        builder = self.get_builder()
        record = builder.order_by("name").first()
        self.assertIsInstance(record, dict)
        self.assertEqual(record["name"], "Bob")
        self.assertEqual(record["id"], 3)

    def test_first_with_columns(self):
        builder = self.get_builder()
        builder.order_by("name").first(["name", "id"], query=True)
        sql = """SELECT "users_query"."name", "users_query"."id" FROM "users_query" ORDER BY "name" ASC LIMIT 1"""
        self.assertEqual(builder.to_sql(), sql)

        # get a new instance of the builder
        # required after instance was used for other task
        builder = self.get_builder()
        record = builder.order_by("name").first(["name", "id"])
        self.assertIsInstance(record, dict)
        self.assertEqual(record["name"], "Bob")
        self.assertEqual(record["id"], 3)
        self.assertTrue("email" not in list(record.keys()))

    def test_last(self):
        builder = self.get_builder()
        builder.order_by("name").last(query=True)
        sql = """SELECT * FROM "users_query" ORDER BY "name" ASC"""
        self.assertEqual(builder.to_sql(), sql)

        # get a new instance of the builder
        # required after instance was used for other task
        builder = self.get_builder()
        record = builder.last()
        self.assertIsInstance(record, dict)
        self.assertEqual(record["name"], "Steve")

    def test_last_with_columns(self):
        builder = self.get_builder()
        # TODO: last() "columns" parameter should be returned fields not order by
        builder.order_by("name").last("name, id", query=True)
        sql = """SELECT "users_query"."name", "users_query"."id" FROM "users_query" ORDER BY "name" ASC LIMIT 1"""
        self.assertEqual(builder.to_sql(), sql)

        # get a new instance of the builder
        # required after instance was used for other task
        builder = self.get_builder()
        record = builder.order_by("name").last(["name", "id"])
        self.assertIsInstance(record, dict)
        self.assertEqual(record["name"], "Steve")
        self.assertEqual(record["id"], 1)
        self.assertTrue("email" not in list(record.keys()))

    def test_first_or_fail_exception(self):
        builder = self.get_builder()
        builder.where("name", "Marlysson").first_or_fail(query=True)
        sql = """SELECT * FROM "users_query" WHERE "users_query"."name" = 'Marlysson' LIMIT 1"""
        self.assertEqual(builder.to_sql(), sql)

        # get a new instance of the builder
        # required after instance was used for other task
        builder = self.get_builder().new()
        with self.assertRaises(ModelNotFound):
            builder.where("name", "Marlysson").first_or_fail()

    def test_find_or_fail_exception(self):
        builder = self.get_builder()
        with self.assertRaises(ModelNotFound):
            builder.find_or_fail(1000)

    def test_find_or_404_exception(self):
        builder = self.get_builder()
        with self.assertRaises(HTTP404):
            builder.find_or_404(10000)

    def test_select_one(self):
        builder = self.get_builder()
        builder.select("name")
        sql = '''SELECT "users_query"."name" FROM "users_query"'''
        self.assertEqual(builder.to_sql(), sql)
        result = builder.get()
        self.assertEqual(result.count(), 3)
        self.assertEqual(list(result.first().keys()), ["name"])

    def test_select_multiple_as_args(self):
        builder = self.get_builder()
        builder.select("name", "email")
        sql = (
            '''SELECT "users_query"."name", "users_query"."email" FROM "users_query"'''
        )
        self.assertEqual(builder.to_sql(), sql)
        result = builder.get()
        self.assertEqual(result.count(), 3)
        self.assertEqual(list(result.first().keys()), ["name", "email"])

    def test_select_multiple_as_string(self):
        builder = self.get_builder()
        builder.select("name, email")
        sql = (
            '''SELECT "users_query"."name", "users_query"."email" FROM "users_query"'''
        )
        self.assertEqual(builder.to_sql(), sql)
        result = builder.get()
        self.assertEqual(result.count(), 3)
        self.assertEqual(list(result.first().keys()), ["name", "email"])

    def test_add_select(self):
        builder = self.get_builder()
        (
            builder.select("name")
            .add_select("phone_count", lambda q: q.count("*").table("phones"))
            .add_select("salary", lambda q: q.count("*").table("salary"))
        )
        sql = '''SELECT "users_query"."name", (SELECT COUNT(*) AS m_count_reserved FROM "phones") AS phone_count, (SELECT COUNT(*) AS m_count_reserved FROM "salary") AS salary FROM "users_query"'''
        self.assertEqual(builder.to_sql(), sql)
        # TODO: add actual data tests

    def test_add_select_no_table(self):
        builder = self.get_builder(table=None)
        (
            builder.add_select(
                "other_test", lambda q: q.max("updated_at").table("different_table")
            ).add_select(
                "some_alias", lambda q: q.max("updated_at").table("another_table")
            )
        )
        sql = (
            "SELECT "
            '(SELECT MAX("different_table"."updated_at") AS updated_at FROM "different_table") AS other_test, '
            '(SELECT MAX("another_table"."updated_at") AS updated_at FROM "another_table") AS some_alias'
        )
        self.assertEqual(builder.to_sql(), sql)
        # TODO: add actual data tests

    def test_add_select_with_raw(self):
        builder = self.get_builder(table=None)
        (
            builder.select_raw("max(updated_at) as test")
            .from_("some_table")
            .add_select(
                "other_test",
                lambda query: (
                    query.max("updated_at")
                    .from_("different_table")
                    .where("some_id", "=", "3")
                ),
            )
        )
        sql = (
            "SELECT max(updated_at) as test, "
            '(SELECT MAX("different_table"."updated_at") AS updated_at '
            'FROM "different_table" '
            'WHERE "different_table"."some_id" = \'3\') AS other_test '
            'FROM "some_table"'
        )
        self.assertEqual(builder.to_sql(), sql)
        # TODO: add actual data tests

    def test_select_raw(self):
        builder = self.get_builder()
        builder.select_raw("count(email) as email_count")
        sql = '''SELECT count(email) as email_count FROM "users_query"'''
        self.assertEqual(builder.to_sql(), sql)
        self.assertEqual(builder.first()["email_count"], 3)

    def test_create_using_dict(self):
        builder = self.get_builder()
        builder_sql = builder.create(
            {"name": "Corentin All", "email": "corentin@yopmail.com", "age": 15},
            query=True,
        ).to_sql()
        sql = """INSERT INTO "users_query" ("name", "email", "age") VALUES ('Corentin All', 'corentin@yopmail.com', '15')"""
        self.assertEqual(builder_sql, sql)

        # get a new instance of the builder
        # required after query=True on original builder instance
        builder = self.get_builder()
        new_record = builder.create(
            {"name": "Corentin All", "email": "corentin@yopmail.com", "age": 15},
        )
        records = builder.where("name", "Corentin All").get()
        self.assertEqual(records.count(), 1)
        self.assertEqual(records.first()["email"], new_record["email"])

    def test_create_using_args(self):
        builder = self.get_builder()
        builder_sql = builder.create(
            name="Corentin All", email="corentin@yopmail.com", age=15, query=True
        ).to_sql()
        sql = """INSERT INTO "users_query" ("name", "email", "age") VALUES ('Corentin All', 'corentin@yopmail.com', '15')"""
        self.assertEqual(builder_sql, sql)

        # get a new instance of the builder
        # required after query=True on original builder instance
        builder = self.get_builder()
        new_record = builder.create(
            name="Corentin All", email="corentin@yopmail.com", age=15
        )
        records = builder.where("name", "Corentin All").get()
        self.assertEqual(records.count(), 1)
        self.assertEqual(records.first()["email"], new_record["email"])

    def test_delete(self):
        builder = self.get_builder()
        builder_sql = builder.delete("name", "Joe", query=True)
        sql = """DELETE FROM "users_query" WHERE "name" = 'Joe\'"""
        self.assertEqual(builder.to_sql(), sql)

        # get a new instance of the builder
        # required after query=True on original builder instance
        builder = self.get_builder()
        builder.delete("name", "Joe")

        records = builder.get()
        self.assertEqual(records.count(), 2)
        self.assertTrue(records.where("name", "Joe").is_empty())

    def test_where(self):
        builder = self.get_builder()
        builder.where("name", "Joe")
        sql = """SELECT * FROM "users_query" WHERE "users_query"."name" = 'Joe\'"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 1)
        self.assertEqual(records.first()["name"], "Joe")

    def test_where_dictionary(self):
        builder = self.get_builder()
        builder.where({"name": "Joe"})
        sql = """SELECT * FROM "users_query" WHERE "users_query"."name" = 'Joe\'"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 1)
        self.assertEqual(records.first()["name"], "Joe")

    def test_where_exists(self):
        builder = self.get_builder()
        builder.where_exists("name")
        # TODO: is this query corect?
        sql = """SELECT * FROM "users_query" WHERE EXISTS 'name\'"""
        self.assertEqual(builder.to_sql(), sql)
        # records = builder.get()
        # self.assertEqual()

    def test_limit(self):
        builder = self.get_builder()
        # add extra records to test limit against
        builder.bulk_create(
            [
                {"name": "George", "age": 3, "email": "george@domain.com"},
                {"name": "Mike", "age": 3, "email": "mike@domain.com"},
                {"name": "James", "age": 3, "email": "james@domain.com"},
                {"name": "Amy", "age": 3, "email": "amy@domain.com"},
                {"name": "Greg", "age": 3, "email": "greg@domain.com"},
            ]
        )

        # get a new instance of the builder
        # required after instance was used for other task
        builder = self.get_builder()
        builder.limit(5)
        sql = """SELECT * FROM "users_query" LIMIT 5"""
        self.assertEqual(builder.to_sql(), sql)
        records = builder.get()
        self.assertEqual(records.count(), 5)

    def test_offset(self):
        builder = self.get_builder()
        # add extra records to test offset against
        builder.bulk_create(
            [
                {"name": "George", "age": 3, "email": "george@domain.com"},
                {"name": "Mike", "age": 3, "email": "mike@domain.com"},
                {"name": "James", "age": 3, "email": "james@domain.com"},
                {"name": "Amy", "age": 3, "email": "amy@domain.com"},
                {"name": "Greg", "age": 3, "email": "greg@domain.com"},
            ]
        )

        # get a new instance of the builder
        # required after instance was used for other task
        builder = self.get_builder()
        builder.offset(5)
        # TODO: is this query correct?
        sql = """SELECT * FROM "users_query" OFFSET 5"""
        self.assertEqual(builder.to_sql(), sql)
        records = builder.get()
        self.assertEqual(records.count(), 3)

    def test_join(self):
        builder = self.get_builder()
        builder.join("profiles", "users.id", "=", "profiles.user_id")
        sql = '''SELECT * FROM "users_query" INNER JOIN "profiles" ON "users"."id" = "profiles"."user_id"'''
        self.assertEqual(builder.to_sql(), sql)
        # TODO: add actual data tests

    def test_left_join(self):
        builder = self.get_builder()
        builder.left_join("profiles", "users.id", "=", "profiles.user_id")
        sql = '''SELECT * FROM "users_query" LEFT JOIN "profiles" ON "users"."id" = "profiles"."user_id"'''
        self.assertEqual(builder.to_sql(), sql)
        # TODO: add actual data tests

    def test_right_join(self):
        builder = self.get_builder()
        builder.right_join("profiles", "users.id", "=", "profiles.user_id")
        sql = '''SELECT * FROM "users_query" LEFT JOIN "profiles" ON "users"."id" = "profiles"."user_id"'''
        self.assertEqual(builder.to_sql(), sql)
        # TODO: add actual data tests

    def test_update(self):
        builder = self.get_builder()
        builder_sql = builder.update(
            {"name": "Joe", "email": "joe@yopmail.com"}, dry=True
        ).to_sql()
        sql = (
            """UPDATE "users_query" SET "name" = 'Joe', "email" = 'joe@yopmail.com\'"""
        )
        self.assertEqual(builder.to_sql(), sql)

        # get a new instance of the builder
        # required after instance was used for other task
        builder = self.get_builder()
        # update ALL records
        updated_record = builder.update({"name": "Joe", "email": "joe@yopmail.com"})
        records = builder.where("name", "Joe").get()
        self.assertEqual(records.count(), 3)
        for user in records:
            self.assertEqual(user["email"], updated_record["email"])

    def test_increment(self):
        builder = self.get_builder()
        original_records = builder.get()

        # TODO: this should have a query= param to allow returing the builder
        builder.increment("age", 2)
        sql = """UPDATE "users_query" SET "age" = "age" + '2\'"""
        self.assertEqual(builder.to_sql(), sql)

        # get a new instance of the builder
        # required after instance was used for other task
        builder = self.get_builder()
        incremented_records = builder.get()
        for record in original_records:
            original_age = int(record["age"])
            test_record = incremented_records.where("id", record["id"]).first()
            incremented_age = int(test_record["age"])
            self.assertEqual(incremented_age, original_age + 2)

    def test_decrement(self):
        builder = self.get_builder()
        original_records = builder.get()
        # TODO: this should have a query= param to allow returing the builder
        builder.decrement("age", 1)
        # sql = '''UPDATE "users_query" SET "age" = "age" - '1\''''
        # self.assertEqual(builder.to_sql(), sql)

        # get a new instance of the builder
        # required after instance was used for other task
        builder = self.get_builder()
        dec_records = builder.get()
        for record in original_records:
            original_age = int(record["age"])
            test_record = dec_records.where("id", record["id"]).first()
            decremented_age = int(test_record["age"])
            self.assertEqual(decremented_age, original_age - 1)

    def test_count(self):
        builder = self.get_builder()
        builder.count("id")
        sql = '''SELECT COUNT("users_query"."id") AS id FROM "users_query"'''
        self.assertEqual(builder.to_sql(), sql)
        record = builder.first()
        self.assertEqual(record["id"], 3)

    def test_order_by_asc(self):
        builder = self.get_builder()
        builder.order_by("name", "asc")
        sql = """SELECT * FROM "users_query" ORDER BY "name" ASC"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.first()["name"], "Bob")

    def test_order_by_desc(self):
        builder = self.get_builder()
        builder.order_by("name", "desc")
        sql = """SELECT * FROM "users_query" ORDER BY "name" DESC"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.first()["name"], "Steve")

    def test_order_by_multiple_asc(self):
        builder = self.get_builder()
        # add extra records to test multi column ordering
        builder.bulk_create(
            [
                {"name": "George", "age": 15, "email": "george@domain.com"},
                {"name": "Mike", "age": 21, "email": "mike@domain.com"},
                {"name": "James", "age": 31, "email": "james@domain.com"},
                {"name": "Amy", "age": 44, "email": "amy@domain.com"},
                {"name": "Simon", "age": 13, "email": "simon@domain.com"},
            ]
        )

        # get a new instance of the builder
        # required after instance was used for other task
        builder = self.get_builder()
        builder.order_by("age, name, email")
        sql = """SELECT * FROM "users_query" ORDER BY "age" ASC, "name" ASC, "email" ASC"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.first()["name"], "Bob")
        self.assertEqual(records.last()["name"], "Amy")

    def test_order_by_mixed_multiple(self):
        builder = self.get_builder()
        # add extra records to test multi column ordering
        builder.bulk_create(
            [
                {"name": "George", "age": 15, "email": "george@domain.com"},
                {"name": "Mike", "age": 21, "email": "mike@domain.com"},
                {"name": "James", "age": 31, "email": "james@domain.com"},
                {"name": "Amy", "age": 44, "email": "amy@domain.com"},
                {"name": "Simon", "age": 13, "email": "simon@domain.com"},
            ]
        )

        # get a new instance of the builder
        # required after instance was used for other task
        builder = self.get_builder()
        builder.order_by("age desc, name, email desc")
        sql = """SELECT * FROM "users_query" ORDER BY "age" DESC, "name" ASC, "email" DESC"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.first()["name"], "Amy")
        self.assertEqual(records.last()["name"], "Steve")

    def test_order_by_raw(self):
        builder = self.get_builder()
        builder.order_by_raw("name desc")
        sql = """SELECT * FROM "users_query" ORDER BY name desc"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.last()["name"], "Bob")

    def test_where_column(self):
        builder = self.get_builder()
        builder.bulk_create(
            [
                {"name": "george@domain.com", "age": 15, "email": "george@domain.com"},
            ]
        )

        # get a new instance of the builder
        # required after instance was used for other task
        builder = self.get_builder()
        builder.where_column("name", "email")
        sql = '''SELECT * FROM "users_query" WHERE "users_query"."name" = "users_query"."email"'''
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 1)
        self.assertEqual(records.first()["name"], "george@domain.com")

    def test_where_not_in(self):
        builder = self.get_builder()
        builder.where_not_in("id", [2])
        sql = """SELECT * FROM "users_query" WHERE "users_query"."id" NOT IN ('2')"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 2)
        for user in records:
            self.assertTrue((user["id"] in [1, 3]))

    def test_between(self):
        builder = self.get_builder()
        builder.between("age", 10, 20)
        sql = """SELECT * FROM "users_query" WHERE "users_query"."age" BETWEEN '10' AND '20\'"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 2)
        for user in records:
            self.assertTrue((int(user["age"]) >= 10 <= 20))

    def test_not_between(self):
        builder = self.get_builder()
        builder.not_between("age", 10, 20)
        sql = """SELECT * FROM "users_query" WHERE "users_query"."age" NOT BETWEEN '10' AND '20\'"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 1)
        self.assertEqual(int(records.first()["age"]), 23)

    def test_where_in(self):
        builder = self.get_builder()
        builder.where_in("id", [1, 3])
        sql = """SELECT * FROM "users_query" WHERE "users_query"."id" IN ('1','3')"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 2)
        for user in records:
            self.assertTrue((user["id"] in [1, 3]))

    def test_where_null(self):
        builder = self.get_builder()
        # add a record with 'name' not set (will be NULL)
        builder.bulk_create(
            [
                {"age": 15, "email": "george@domain.com"},
            ]
        )

        # get a new instance of the builder
        # required after instance was used for other task
        builder = self.get_builder()
        builder.where_null("name")
        sql = """SELECT * FROM "users_query" WHERE "users_query"."name" IS NULL"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 1)
        self.assertEqual(records.first()["email"], "george@domain.com")

    def test_where_not_null(self):
        builder = self.get_builder()
        builder.where_not_null("name")
        sql = """SELECT * FROM "users_query" WHERE "users_query"."name" IS NOT NULL"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 3)

    def test_having(self):
        builder = self.get_builder(table="payments")
        builder.select("user_id").avg("salary").group_by("user_id").having(
            "salary", ">=", "1000"
        )

        sql = """SELECT "payments"."user_id", AVG("payments"."salary") AS salary FROM "payments" GROUP BY "payments"."user_id" HAVING "payments"."salary" >= '1000\'"""
        self.assertEqual(builder.to_sql(), sql)

    def test_group_by(self):
        builder = self.get_builder(table="payments")
        builder.select("user_id").min("salary").group_by("user_id")
        sql = '''SELECT "payments"."user_id", MIN("payments"."salary") AS salary FROM "payments" GROUP BY "payments"."user_id"'''
        self.assertEqual(builder.to_sql(), sql)
        # TODO: add testing frm saved data

    def test_group_by_raw(self):
        builder = self.get_builder(table="payments")
        builder.select("user_id").min("salary").group_by_raw("count(*)")

        sql = """SELECT "payments"."user_id", MIN("payments"."salary") AS salary FROM "payments" GROUP BY count(*)"""
        self.assertEqual(builder.to_sql(), sql)
        # TODO: add testing frm saved data

    def test_group_by_multiple(self):
        builder = self.get_builder(table="payments")
        builder.select("user_id").min("salary").group_by("user_id").group_by("salary")

        sql = '''SELECT "payments"."user_id", MIN("payments"."salary") AS salary FROM "payments" GROUP BY "payments"."user_id", "payments"."salary"'''
        self.assertEqual(builder.to_sql(), sql)
        # TODO: add testing frm saved data

    def test_group_by_multiple_in_same_group_by(self):
        builder = self.get_builder(table="payments")
        builder.select("user_id").min("salary").group_by("user_id, salary")

        sql = '''SELECT "payments"."user_id", MIN("payments"."salary") AS salary FROM "payments" GROUP BY "payments"."user_id", "payments"."salary"'''
        self.assertEqual(builder.to_sql(), sql)

    def test_builder_alone(self):
        builder = QueryBuilder(
            connection_details={
                "default": "sqlite",
                "sqlite": {
                    "driver": "sqlite",
                    "database": "orm.sqlite3",
                    "prefix": "",
                },
            }
        ).table("users_query")
        sql = '''SELECT * FROM "users_query"'''
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 3)

    def test_where_lt(self):
        builder = self.get_builder()
        builder.where("age", "<", "20")
        sql = """SELECT * FROM "users_query" WHERE "users_query"."age" < '20\'"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 2)

    def test_where_lte(self):
        builder = self.get_builder()
        builder.where("age", "<=", "23")
        sql = """SELECT * FROM "users_query" WHERE "users_query"."age" <= '23\'"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 3)

    def test_where_gt(self):
        builder = self.get_builder()
        builder.where("age", ">", "20")
        sql = """SELECT * FROM "users_query" WHERE "users_query"."age" > '20\'"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 1)

    def test_latest(self):
        builder = self.get_builder()
        builder.latest("email")
        sql = """SELECT * FROM "users_query" ORDER BY "email" DESC"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 3)
        self.assertEqual(records.first()["email"], "steve@domain.com")

    def test_oldest(self):
        builder = self.get_builder()
        builder.oldest("email")
        sql = """SELECT * FROM "users_query" ORDER BY "email" ASC"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 3)
        self.assertEqual(records.first()["email"], "bob@domain.com")

    def test_where_gte(self):
        builder = self.get_builder()
        builder.where("age", ">=", "13")
        sql = """SELECT * FROM "users_query" WHERE "users_query"."age" >= '13\'"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 3)

    def test_where_ne(self):
        builder = self.get_builder()
        builder.where("age", "!=", "13")
        sql = """SELECT * FROM "users_query" WHERE "users_query"."age" != '13\'"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 1)

    def test_or_where(self):
        builder = self.get_builder()
        builder.where("age", "20").or_where("age", "<", 19)
        sql = """SELECT * FROM "users_query" WHERE "users_query"."age" = '20' OR "users_query"."age" < '19\'"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 2)

    def test_can_call_with_schema(self):
        builder = self.get_builder()
        builder.table("sqlite_schema").select("tbl_name").where(
            "tbl_name", "users_query"
        )
        sql = """SELECT "sqlite_schema"."tbl_name" FROM "sqlite_schema" WHERE "sqlite_schema"."tbl_name" = 'users_query\'"""
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 1)

    def test_can_call_with_raw(self):
        builder = self.get_builder()
        builder.statement("select * from users_query")
        sql = '''SELECT * FROM "users_query"'''
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 3)

    def test_truncate(self):
        builder = self.get_builder()
        # TODO: add query= param to truncate to return query builder
        builder.truncate()
        sql = '''DELETE FROM "users_query"'''
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 0)

    def test_truncate_without_foreign_keys(self):
        builder = self.get_builder()
        # TODO: add query= param to truncate to return query builder
        builder.truncate(foreign_keys=True)
        sql = [
            "PRAGMA foreign_keys = OFF",
            'DELETE FROM "users_query"',
            "PRAGMA foreign_keys = ON",
        ]
        self.assertEqual(builder.to_sql(), sql)

        records = builder.get()
        self.assertEqual(records.count(), 0)

    def test_when(self):
        builder = self.get_builder()
        # TODO: investigate when
        builder.when(19 > 18, lambda q: q.where("age_restricted", 1))
        sql = """SELECT * FROM "users_query" WHERE "users_query"."age_restricted" = '1\'"""
        self.assertEqual(builder.to_sql(), sql)

        builder = self.get_builder()
        builder.when(17 > 18, lambda q: q.where("age_restricted", 0))
        sql = '''SELECT * FROM "users_query"'''
        self.assertEqual(builder.to_sql(), sql)
