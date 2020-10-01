import inspect
import unittest

from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import PostgresGrammar
from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.models import Model
from tests.utils import MockConnectionFactory


class MockConnection:

    connection_details = {}

    def make_connection(self):
        return self

    @classmethod
    def get_default_query_grammar(cls):
        return


class BaseTestQueryBuilder:
    def get_builder(self, table="users"):
        connection = MockConnectionFactory().make("default")
        return QueryBuilder(self.grammar, connection, table=table, model=Model())

    def test_sum(self):
        builder = self.get_builder()
        builder.sum("age")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_max(self):
        builder = self.get_builder()
        builder.max("age")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_min(self):
        builder = self.get_builder()
        builder.min("age")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_avg(self):
        builder = self.get_builder()
        builder.avg("age")
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_all(self):
        builder = self.get_builder()
        builder.all()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_get(self):
        builder = self.get_builder()
        builder.get()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_first(self):
        builder = self.get_builder().first(query=True)
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_select(self):
        builder = self.get_builder()
        builder.select("name", "email")
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_select_raw(self):
        builder = self.get_builder()
        builder.select_raw("count(email) as email_count")
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_create(self):
        builder = self.get_builder().without_global_scopes()
        builder.create(
            {"name": "Corentin All", "email": "corentin@yopmail.com"}, query=True
        )
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_delete(self):
        builder = self.get_builder()
        builder.delete("name", "Joe", query=True)
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_where(self):
        builder = self.get_builder()
        builder.where("name", "Joe")
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_where_exists(self):
        builder = self.get_builder()
        builder.where_exists("name")
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_limit(self):
        builder = self.get_builder()
        builder.limit(5)
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_offset(self):
        builder = self.get_builder()
        builder.offset(5)
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_join(self):
        builder = self.get_builder()
        builder.join("profiles", "users.id", "=", "profiles.user_id")
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_left_join(self):
        builder = self.get_builder()
        builder.left_join("profiles", "users.id", "=", "profiles.user_id")
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_right_join(self):
        builder = self.get_builder()
        builder.right_join("profiles", "users.id", "=", "profiles.user_id")
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_update(self):
        builder = self.get_builder().update(
            {"name": "Joe", "email": "joe@yopmail.com"}, dry=True
        )
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_increment(self):
        builder = self.get_builder()
        builder.increment("age", 1)
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_decrement(self):
        builder = self.get_builder()
        builder.decrement("age", 1)
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_count(self):
        builder = self.get_builder()
        builder.count("id")
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_order_by_asc(self):
        builder = self.get_builder()
        builder.order_by("email", "asc")
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_order_by_desc(self):
        builder = self.get_builder()
        builder.order_by("email", "desc")
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_where_column(self):
        builder = self.get_builder()
        builder.where_column("name", "username")
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_where_not_in(self):
        builder = self.get_builder()
        builder.where_not_in("id", [1, 2, 3])
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_between(self):
        builder = self.get_builder()
        builder.between("id", 2, 5)
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_not_between(self):
        builder = self.get_builder()
        builder.not_between("id", 2, 5)
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_where_in(self):
        builder = self.get_builder()
        builder.where_in("id", [1, 2, 3])

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_where_null(self):
        builder = self.get_builder()
        builder.where_null("name")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_where_not_null(self):
        builder = self.get_builder()
        builder.where_not_null("name")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_having(self):
        builder = self.get_builder(table="payments")
        builder.select("user_id").avg("salary").group_by("user_id").having(
            "salary", ">=", "1000"
        )

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_group_by(self):
        builder = self.get_builder(table="payments")
        builder.select("user_id").min("salary").group_by("user_id")

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_builder_alone(self):
        self.assertTrue(
            QueryBuilder(
                connection=MockConnection,
                connection_details={
                    "default": "postgres",
                    "postgres": {
                        "driver": "postgres",
                        "host": "localhost",
                        "user": "postgres",
                        "password": "postgres",
                        "database": "orm",
                        "port": "5432",
                        "prefix": "",
                        "grammar": "postgres",
                    },
                },
            ).table("users")
        )

    def test_where_lt(self):
        builder = self.get_builder()
        builder.where("age", "<", "20")
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_where_lte(self):
        builder = self.get_builder()
        builder.where("age", "<=", "20")
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_where_gt(self):
        builder = self.get_builder()
        builder.where("age", ">", "20")
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_where_gte(self):
        builder = self.get_builder()
        builder.where("age", ">=", "20")
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_where_ne(self):
        builder = self.get_builder()
        builder.where("age", "!=", "20")
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_or_where(self):
        builder = self.get_builder()
        builder.where("age", "20").or_where("age", "<", 20)
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)


class PostgresQueryBuilderTest(BaseTestQueryBuilder, unittest.TestCase):

    grammar = PostgresGrammar

    def sum(self):
        """
        builder = self.get_builder()
        builder.sum('age')
        """
        return """SELECT SUM("users"."age") AS age FROM "users\""""

    def max(self):
        """
        builder = self.get_builder()
        builder.max('age')
        """
        return """SELECT MAX("users"."age") AS age FROM "users\""""

    def min(self):
        """
        builder = self.get_builder()
        builder.min('age')
        """
        return """SELECT MIN("users"."age") AS age FROM "users\""""

    def avg(self):
        """
        builder = self.get_builder()
        builder.avg('age')
        """
        return """SELECT AVG("users"."age") AS age FROM "users\""""

    def first(self):
        """
        builder = self.get_builder()
        builder.first()
        """
        return """SELECT * FROM "users" LIMIT 1"""

    def all(self):
        """
        builder = self.get_builder()
        builder.all()
        """
        return """SELECT * FROM "users\""""

    def get(self):
        """
        builder = self.get_builder()
        builder.get()
        """
        return """SELECT * FROM "users\""""

    def select(self):
        """
        builder = self.get_builder()
        builder.select('name', 'email')
        """
        return """SELECT "users"."name", "users"."email" FROM "users\""""

    def select_raw(self):
        """
        builder = self.get_builder()
        builder.select_raw('count(email) as email_count')
        """
        return """SELECT count(email) as email_count FROM "users\""""

    def create(self):
        """
        builder = get_builder()
        builder.create({"name": "Corentin All", 'email': 'corentin@yopmail.com'})
        """
        return """INSERT INTO "users" ("name", "email") VALUES ('Corentin All', 'corentin@yopmail.com') RETURNING *"""

    def delete(self):
        """
        builder = get_builder()
        builder.delete("name', 'Joe')
        """
        return """DELETE FROM "users" WHERE "users"."name" = 'Joe'"""

    def where(self):
        """
        builder = get_builder()
        builder.where('name', 'Joe')
        """
        return """SELECT * FROM "users" WHERE "users"."name" = 'Joe'"""

    def where_exists(self):
        """
        builder = get_builder()
        builder.where_exists('name')
        """
        return """SELECT * FROM "users" WHERE EXISTS 'name'"""

    def limit(self):
        """
        builder = get_builder()
        builder.limit(5)
        """
        return """SELECT * FROM "users" LIMIT 5"""

    def offset(self):
        """
        builder = get_builder()
        builder.offset(5)
        """
        return """SELECT * FROM "users" OFFSET 5"""

    def join(self):
        """
        builder.join("profiles", "users.id", "=", "profiles.user_id")
        """
        return """SELECT * FROM "users" INNER JOIN "profiles" ON "users"."id" = "profiles"."user_id\""""

    def left_join(self):
        """
        builder.left_join("profiles", "users.id", "=", "profiles.user_id")
        """
        return """SELECT * FROM "users" LEFT JOIN "profiles" ON "users"."id" = "profiles"."user_id\""""

    def right_join(self):
        """
        builder.right_join("profiles", "users.id", "=", "profiles.user_id")
        """
        return """SELECT * FROM "users" RIGHT JOIN "profiles" ON "users"."id" = "profiles"."user_id\""""

    def update(self):
        """
        builder.update({"name": "Joe", "email": "joe@yopmail.com"})
        """
        return """UPDATE "users" SET "name" = 'Joe', "email" = 'joe@yopmail.com'"""

    def increment(self):
        """
        builder.increment('age', 1)
        """
        return """UPDATE "users" SET "age" = "age" + '1'"""

    def decrement(self):
        """
        builder.decrement('age', 1)
        """
        return """UPDATE "users" SET "age" = "age" - '1'"""

    def count(self):
        """
        builder.count(id)
        """
        return """SELECT COUNT("users"."id") AS id FROM "users\""""

    def order_by_asc(self):
        """
        builder.order_by('email', 'asc')
        """
        return """SELECT * FROM "users" ORDER BY "users"."email" ASC"""

    def order_by_desc(self):
        """
        builder.order_by('email', 'des')
        """
        return """SELECT * FROM "users" ORDER BY "users"."email" DESC"""

    def where_column(self):
        """
        builder.where_column('name', 'username')
        """
        return """SELECT * FROM "users" WHERE "users"."name" = "users"."username\""""

    def where_null(self):
        """
        builder.where_null('name')
        """
        return """SELECT * FROM "users" WHERE "users"."name" IS NULL"""

    def where_not_null(self):
        """
        builder.where_null('name')
        """
        return """SELECT * FROM "users" WHERE "users"."name" IS NOT NULL"""

    def where_not_in(self):
        """
        builder.where_not_in('id', [1, 2, 3])
        """
        return """SELECT * FROM "users" WHERE "users"."id" NOT IN ('1','2','3')"""

    def where_in(self):
        """
        builder.where_in('id', [1, 2, 3])
        """
        return """SELECT * FROM "users" WHERE "users"."id" IN ('1','2','3')"""

    def between(self):
        """
        builder.between('id', 2, 5)
        """
        return """SELECT * FROM "users" WHERE "users"."id" BETWEEN '2' AND '5'"""

    def not_between(self):
        """
        builder.not_between('id', 2, 5)
        """
        return """SELECT * FROM "users" WHERE "users"."id" NOT BETWEEN '2' AND '5'"""

    def having(self):
        """
        builder.select('user_id').avg('salary').group_by('user_id').having('salary', '>=', '1000')
        """
        return """SELECT "payments"."user_id", AVG("payments"."salary") AS salary FROM "payments" GROUP BY "payments"."user_id" HAVING "payments"."salary" >= '1000'"""

    def group_by(self):
        """
        builder.select('user_id').min('salary').group_by('user_id')
        """
        return """SELECT "payments"."user_id", MIN("payments"."salary") AS salary FROM "payments" GROUP BY "payments"."user_id\""""

    def where_lt(self):
        """
        builder = self.get_builder()
        builder.where('age', '<', '20')
        """
        return """SELECT * FROM "users" WHERE "users"."age" < '20'"""

    def where_lte(self):
        """
        builder = self.get_builder()
        builder.where('age', '<=', '20')
        """
        return """SELECT * FROM "users" WHERE "users"."age" <= '20'"""

    def where_gt(self):
        """
        builder = self.get_builder()
        builder.where('age', '>', '20')
        """
        return """SELECT * FROM "users" WHERE "users"."age" > '20'"""

    def where_gte(self):
        """
        builder = self.get_builder()
        builder.where('age', '>=', '20')
        """
        return """SELECT * FROM "users" WHERE "users"."age" >= '20'"""

    def where_ne(self):
        """
        builder = self.get_builder()
        builder.where('age', '!=', '20')
        """
        return """SELECT * FROM "users" WHERE "users"."age" != '20'"""

    def or_where(self):
        """
        builder = self.get_builder()
        builder.where('age', '20').or_where('age','<', 20)
        """
        return """SELECT * FROM "users" WHERE "users"."age" = '20' OR "users"."age" < '20'"""
