import inspect
import unittest

from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import PostgresGrammar
from tests.utils import MockConnectionFactory


class MockConnection:

    connection_details = {}

    def make_connection(self):
        return self

    @classmethod
    def get_default_query_grammar(cls):
        return


class ModelTest(Model):
    __timestamps__ = False


class TestMSSQLQueryBuilder(unittest.TestCase):
    maxDiff = None

    def get_builder(self, table="users", dry=True):
        connection = MockConnectionFactory().make("mssql")
        return QueryBuilder(
            # self.grammar,
            connection_class=connection,
            connection="mssql",
            table=table,
            model=ModelTest(),
            dry=dry,
        )

    def test_sum(self):
        builder = self.get_builder()
        builder.sum("age")

        self.assertEqual(
            builder.to_sql(), "SELECT SUM([users].[age]) AS age FROM [users]"
        )

    def test_where_like(self):
        builder = self.get_builder()
        builder.where("age", "like", "%name%")

        self.assertEqual(
            builder.to_sql(), "SELECT * FROM [users] WHERE [users].[age] LIKE '%name%'"
        )

    def test_where_not_like(self):
        builder = self.get_builder()
        builder.where("age", "not like", "%name%")

        self.assertEqual(
            builder.to_sql(),
            "SELECT * FROM [users] WHERE [users].[age] NOT LIKE '%name%'",
        )

    def test_max(self):
        builder = self.get_builder()
        builder.max("age")

        self.assertEqual(
            builder.to_sql(), "SELECT MAX([users].[age]) AS age FROM [users]"
        )

    def test_min(self):
        builder = self.get_builder()
        builder.min("age")

        self.assertEqual(
            builder.to_sql(), "SELECT MIN([users].[age]) AS age FROM [users]"
        )

    def test_avg(self):
        builder = self.get_builder()
        builder.avg("age")

        self.assertEqual(
            builder.to_sql(), "SELECT AVG([users].[age]) AS age FROM [users]"
        )

    def test_all(self):
        builder = self.get_builder()
        builder.all()

        self.assertEqual(builder.to_sql(), "SELECT * FROM [users]")

    def test_get(self):
        builder = self.get_builder()
        builder.get()

        self.assertEqual(builder.to_sql(), "SELECT * FROM [users]")

    def test_first(self):
        builder = self.get_builder().first(query=True)

        self.assertEqual(builder.to_sql(), "SELECT TOP 1 * FROM [users]")

    def test_select(self):
        builder = self.get_builder()
        builder.select("name", "email")

        self.assertEqual(
            builder.to_sql(), "SELECT [users].[name], [users].[email] FROM [users]"
        )

    def test_add_select_no_table(self):
        builder = self.get_builder(table=None)
        builder.add_select(
            "other_test", lambda q: q.max("updated_at").table("different_table")
        ).add_select("some_alias", lambda q: q.max("updated_at").table("another_table"))

        self.assertEqual(
            builder.to_sql(),
            (
                "SELECT "
                "(SELECT MAX([different_table].[updated_at]) AS updated_at FROM [different_table]) AS other_test, "
                "(SELECT MAX([another_table].[updated_at]) AS updated_at FROM [another_table]) AS some_alias"
            ),
        )

    def test_select_raw(self):
        builder = self.get_builder()
        builder.select_raw("count(email) as email_count")

        self.assertEqual(
            builder.to_sql(), "SELECT count(email) as email_count FROM [users]"
        )

    def test_create(self):
        builder = self.get_builder().without_global_scopes()
        builder.create(
            {"name": "Corentin All", "email": "corentin@yopmail.com"}, query=True
        )

        self.assertEqual(
            builder.to_sql(),
            "INSERT INTO [users] ([users].[name], [users].[email]) VALUES ('Corentin All', 'corentin@yopmail.com')",
        )

    def test_delete(self):
        builder = self.get_builder()
        builder.delete("name", "Joe", query=True)
        self.assertEqual(
            builder.to_sql(), "DELETE FROM [users] WHERE [users].[name] = 'Joe'"
        )

    def test_where(self):
        builder = self.get_builder()
        builder.where("name", "Joe")

        self.assertEqual(
            builder.to_sql(), "SELECT * FROM [users] WHERE [users].[name] = 'Joe'"
        )

    def test_where_exists(self):
        builder = self.get_builder()
        builder.where_exists("name")
        self.assertEqual(builder.to_sql(), "SELECT * FROM [users] WHERE EXISTS 'name'")

    def test_limit(self):
        builder = self.get_builder()
        builder.limit(5)

        self.assertEqual(builder.to_sql(), "SELECT TOP 5 * FROM [users]")

    def test_offset(self):
        builder = self.get_builder()
        builder.offset(5)

        self.assertEqual(
            builder.to_sql(),
            "SELECT * FROM [users] OFFSET 5 ROWS FETCH NEXT 1 ROWS ONLY",
        )

    def test_join(self):
        builder = self.get_builder()
        builder.join("profiles", "users.id", "=", "profiles.user_id")

        self.assertEqual(
            builder.to_sql(),
            "SELECT * FROM [users] INNER JOIN [profiles] ON [users].[id] = [profiles].[user_id]",
        )

    def test_left_join(self):
        builder = self.get_builder()
        builder.left_join("profiles", "users.id", "=", "profiles.user_id")
        self.assertEqual(
            builder.to_sql(),
            "SELECT * FROM [users] LEFT JOIN [profiles] ON [users].[id] = [profiles].[user_id]",
        )

    def test_right_join(self):
        builder = self.get_builder()
        builder.right_join("profiles", "users.id", "=", "profiles.user_id")
        self.assertEqual(
            builder.to_sql(),
            "SELECT * FROM [users] RIGHT JOIN [profiles] ON [users].[id] = [profiles].[user_id]",
        )

    def test_update(self):
        builder = self.get_builder().update(
            {"name": "Joe", "email": "joe@yopmail.com"}, dry=True
        )
        self.assertEqual(
            builder.to_sql(),
            "UPDATE [users] SET [users].[name] = 'Joe', [users].[email] = 'joe@yopmail.com'",
        )

    def test_increment(self):
        builder = self.get_builder()
        builder.increment("age", 1)
        self.assertEqual(
            builder.to_sql(), "UPDATE [users] SET [users].[age] = [users].[age] + '1'"
        )

    def test_decrement(self):
        builder = self.get_builder()
        builder.decrement("age", 1)
        self.assertEqual(
            builder.to_sql(), "UPDATE [users] SET [users].[age] = [users].[age] - '1'"
        )

    def test_count(self):
        builder = self.get_builder()
        builder.count("id")
        self.assertEqual(
            builder.to_sql(), "SELECT COUNT([users].[id]) AS id FROM [users]"
        )

    def test_order_by_asc(self):
        builder = self.get_builder()
        builder.order_by("email", "asc")
        self.assertEqual(builder.to_sql(), "SELECT * FROM [users] ORDER BY [email] ASC")

    def test_order_by_desc(self):
        builder = self.get_builder()
        builder.order_by("email", "desc")
        self.assertEqual(
            builder.to_sql(), "SELECT * FROM [users] ORDER BY [email] DESC"
        )

    def test_where_column(self):
        builder = self.get_builder()
        builder.where_column("name", "username")
        self.assertEqual(
            builder.to_sql(),
            "SELECT * FROM [users] WHERE [users].[name] = [users].[username]",
        )

    def test_where_not_in(self):
        builder = self.get_builder()
        builder.where_not_in("id", [1, 2, 3])
        self.assertEqual(
            builder.to_sql(),
            "SELECT * FROM [users] WHERE [users].[id] NOT IN ('1','2','3')",
        )

    def test_between(self):
        builder = self.get_builder()
        builder.between("id", 2, 5)
        self.assertEqual(
            builder.to_sql(),
            "SELECT * FROM [users] WHERE [users].[id] BETWEEN '2' AND '5'",
        )

    def test_not_between(self):
        builder = self.get_builder()
        builder.not_between("id", 2, 5)
        self.assertEqual(
            builder.to_sql(),
            "SELECT * FROM [users] WHERE [users].[id] NOT BETWEEN '2' AND '5'",
        )

    def test_where_in(self):
        builder = self.get_builder()
        builder.where_in("id", [1, 2, 3])

        self.assertEqual(
            builder.to_sql(),
            "SELECT * FROM [users] WHERE [users].[id] IN ('1','2','3')",
        )

    def test_where_null(self):
        builder = self.get_builder()
        builder.where_null("name")

        self.assertEqual(
            builder.to_sql(), "SELECT * FROM [users] WHERE [users].[name] IS NULL"
        )

    def test_where_not_null(self):
        builder = self.get_builder()
        builder.where_not_null("name")

        self.assertEqual(
            builder.to_sql(), "SELECT * FROM [users] WHERE [users].[name] IS NOT NULL"
        )

    def test_having(self):
        builder = self.get_builder(table="payments")
        builder.select("user_id").avg("salary").group_by("user_id").having(
            "salary", ">=", "1000"
        )

        self.assertEqual(
            builder.to_sql(),
            "SELECT [payments].[user_id], AVG([payments].[salary]) AS salary FROM [payments] GROUP BY [payments].[user_id] HAVING [payments].[salary] >= '1000'",
        )

    def test_group_by(self):
        builder = self.get_builder(table="payments")
        builder.select("user_id").min("salary").group_by("user_id")

        self.assertEqual(
            builder.to_sql(),
            "SELECT [payments].[user_id], MIN([payments].[salary]) AS salary FROM [payments] GROUP BY [payments].[user_id]",
        )

    def test_builder_alone(self):
        self.assertTrue(
            QueryBuilder(
                connection_class=MockConnection,
                connection="mssql",
                connection_details={
                    "default": "mssql",
                    "mssql": {
                        "driver": "mssql",
                        "host": "localhost",
                        "user": "root",
                        "password": "root",
                        "database": "orm",
                        "port": "5432",
                        "prefix": "",
                        "grammar": "mssql",
                    },
                },
            ).table("users")
        )

    def test_where_lt(self):
        builder = self.get_builder()
        builder.where("age", "<", "20")
        self.assertEqual(
            builder.to_sql(), "SELECT * FROM [users] WHERE [users].[age] < '20'"
        )

    def test_where_lte(self):
        builder = self.get_builder()
        builder.where("age", "<=", "20")
        self.assertEqual(
            builder.to_sql(), "SELECT * FROM [users] WHERE [users].[age] <= '20'"
        )

    def test_where_gt(self):
        builder = self.get_builder()
        builder.where("age", ">", "20")
        self.assertEqual(
            builder.to_sql(), "SELECT * FROM [users] WHERE [users].[age] > '20'"
        )

    def test_where_gte(self):
        builder = self.get_builder()
        builder.where("age", ">=", "20")
        self.assertEqual(
            builder.to_sql(), "SELECT * FROM [users] WHERE [users].[age] >= '20'"
        )

    def test_where_ne(self):
        builder = self.get_builder()
        builder.where("age", "!=", "20")
        self.assertEqual(
            builder.to_sql(), "SELECT * FROM [users] WHERE [users].[age] != '20'"
        )

    def test_or_where(self):
        builder = self.get_builder()
        builder.where("age", "20").or_where("age", "<", 20)
        self.assertEqual(
            builder.to_sql(),
            "SELECT * FROM [users] WHERE [users].[age] = '20' OR [users].[age] < '20'",
        )

    def test_can_call_with_schema(self):
        builder = self.get_builder()
        sql = (
            builder.table("information_schema.columns")
            .select("table_name")
            .where("table_name", "users")
            .to_sql()
        )
        self.assertEqual(
            sql,
            """SELECT [information_schema].[columns].[table_name] FROM [information_schema].[columns] WHERE [information_schema].[columns].[table_name] = 'users'""",
        )

    def test_truncate(self):
        builder = self.get_builder(dry=True)
        sql = builder.truncate()
        self.assertEqual(sql, "TRUNCATE TABLE [users]")

    def test_truncate_without_foreign_keys(self):
        builder = self.get_builder(dry=True)
        sql = builder.truncate(foreign_keys=True)
        self.assertEqual(sql, "TRUNCATE TABLE [users]")
