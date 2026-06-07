import unittest

from src.masoniteorm.exceptions import InvalidArgument
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import MySQLGrammar
from src.masoniteorm.relationships import has_many
from tests.integrations.config.database import DATABASES
from tests.utils import MockConnectionFactory


class Articles(Model):
    pass


class User(Model):
    __timestamps__ = False

    @has_many("id", "user_id")
    def articles(self):
        return Articles


class MySQLQueryBuilderTest(unittest.TestCase):
    """Tests for the QueryBuilder using the MySQL grammar.

    Each test builds a query and asserts the expected SQL inline.
    """

    maxDiff = None

    def get_builder(self, table="users", dry=True):
        connection = MockConnectionFactory().make("default")
        return QueryBuilder(
            grammar=MySQLGrammar,
            connection_class=connection,
            connection="t",
            table=table,
            model=User(),
            dry=dry,
            connection_details=DATABASES,
        )

    # ------------------------------------------------------------------
    # Aggregates
    # ------------------------------------------------------------------

    def test_sum(self):
        builder = self.get_builder()
        builder.sum("age")
        query_sql = builder.to_sql()
        expected_sql = "SELECT SUM(`users`.`age`) AS age FROM `users`"
        self.assertEqual(query_sql, expected_sql)

    def test_sum_chained(self):
        builder = self.get_builder()
        builder.sum("age").max("salary")
        query_sql = builder.to_sql()
        expected_sql = "SELECT SUM(`users`.`age`) AS age, MAX(`users`.`salary`) AS salary FROM `users`"
        self.assertEqual(query_sql, expected_sql)

    def test_with_(self):
        builder = self.get_builder()
        builder.with_("articles").sum("age")
        query_sql = builder.to_sql()
        expected_sql = "SELECT SUM(`users`.`age`) AS age FROM `users`"
        self.assertEqual(query_sql, expected_sql)

    def test_max(self):
        builder = self.get_builder()
        builder.max("age")
        query_sql = builder.to_sql()
        expected_sql = "SELECT MAX(`users`.`age`) AS age FROM `users`"
        self.assertEqual(query_sql, expected_sql)

    def test_min(self):
        builder = self.get_builder()
        builder.min("age")
        query_sql = builder.to_sql()
        expected_sql = "SELECT MIN(`users`.`age`) AS age FROM `users`"
        self.assertEqual(query_sql, expected_sql)

    def test_avg(self):
        builder = self.get_builder()
        builder.avg("age")
        query_sql = builder.to_sql()
        expected_sql = "SELECT AVG(`users`.`age`) AS age FROM `users`"
        self.assertEqual(query_sql, expected_sql)

    def test_count(self):
        builder = self.get_builder()
        builder.count("id")
        query_sql = builder.to_sql()
        expected_sql = "SELECT COUNT(`users`.`id`) AS id FROM `users`"
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # Fetch operations
    # ------------------------------------------------------------------

    def test_all(self):
        builder = self.get_builder()
        builder.all()
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users`"
        self.assertEqual(query_sql, expected_sql)

    def test_get(self):
        builder = self.get_builder()
        builder.get()
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users`"
        self.assertEqual(query_sql, expected_sql)

    def test_first(self):
        builder = self.get_builder().first(query=True)
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` LIMIT 1"
        self.assertEqual(query_sql, expected_sql)

    def test_find_with_model(self):
        builder = self.get_builder()
        builder.find(1000, query=True)
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`id` = '1000'"
        self.assertEqual(query_sql, expected_sql)

    def test_find_with_model_and_list(self):
        builder = self.get_builder()
        builder.find([1000, 2000, 3000], query=True)
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`id` IN ('1000','2000','3000')"
        self.assertEqual(query_sql, expected_sql)

    def test_find_with_model_custom_column(self):
        builder = self.get_builder()
        builder.find(10, column="age", query=True)
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`age` = '10'"
        self.assertEqual(query_sql, expected_sql)

    def test_find_with_builder(self):
        builder = self.get_builder()
        builder._model = None
        builder.find(10, column="age", query=True)
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`age` = '10'"
        self.assertEqual(query_sql, expected_sql)

    def test_find_with_builder_and_list(self):
        builder = self.get_builder()
        builder._model = None
        builder.find([10, 20, 30], column="age", query=True)
        query_sql = builder.to_sql()
        expected_sql = (
            "SELECT * FROM `users` WHERE `users`.`age` IN ('10','20','30')"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_find_with_builder_without_column(self):
        builder = self.get_builder()
        builder._model = None
        with self.assertRaises(InvalidArgument):
            builder.find(10, query=True)

    # ------------------------------------------------------------------
    # SELECT columns
    # ------------------------------------------------------------------

    def test_select(self):
        builder = self.get_builder()
        builder.select("name", "email")
        query_sql = builder.to_sql()
        expected_sql = "SELECT `users`.`name`, `users`.`email` FROM `users`"
        self.assertEqual(query_sql, expected_sql)

    def test_select_with_table(self):
        builder = self.get_builder()
        builder.select("users.*")
        query_sql = builder.to_sql()
        expected_sql = "SELECT `users`.* FROM `users`"
        self.assertEqual(query_sql, expected_sql)

    def test_select_with_table_raw(self):
        builder = self.get_builder()
        builder.select("users.*").from_raw("orders, customers")
        query_sql = builder.to_sql()
        expected_sql = "SELECT `users`.* FROM orders, customers"
        self.assertEqual(query_sql, expected_sql)

    def test_select_with_alias(self):
        builder = self.get_builder()
        builder.select("users.username as name")
        query_sql = builder.to_sql()
        expected_sql = "SELECT `users`.`username` AS name FROM `users`"
        self.assertEqual(query_sql, expected_sql)

    def test_select_raw(self):
        builder = self.get_builder()
        builder.select_raw("count(email) as email_count")
        query_sql = builder.to_sql()
        expected_sql = "SELECT count(email) as email_count FROM `users`"
        self.assertEqual(query_sql, expected_sql)

    def test_add_select(self):
        builder = self.get_builder()
        builder.select("name").add_select(
            "phone_count", lambda q: q.count("*").table("phones")
        ).add_select("salary", lambda q: q.count("*").table("salary"))
        query_sql = builder.to_sql()
        expected_sql = (
            "SELECT `users`.`name`,"
            " (SELECT COUNT(*) AS m_count_reserved FROM `phones`) AS phone_count,"
            " (SELECT COUNT(*) AS m_count_reserved FROM `salary`) AS salary"
            " FROM `users`"
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
            "(SELECT MAX(`different_table`.`updated_at`) AS updated_at FROM `different_table`) AS other_test, "
            "(SELECT MAX(`another_table`.`updated_at`) AS updated_at FROM `another_table`) AS some_alias"
        )
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # WHERE
    # ------------------------------------------------------------------

    def test_where(self):
        builder = self.get_builder()
        builder.where("name", "Joe")
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`name` = 'Joe'"
        self.assertEqual(query_sql, expected_sql)

    def test_where_exists(self):
        builder = self.get_builder()
        builder.where_exists("name")
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` WHERE EXISTS 'name'"
        self.assertEqual(query_sql, expected_sql)

    def test_where_like_as_operator(self):
        builder = self.get_builder()
        builder.where("age", "like", "%name%")
        query_sql = builder.to_sql()
        expected_sql = (
            "SELECT * FROM `users` WHERE `users`.`age` LIKE '%name%'"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_where_like(self):
        builder = self.get_builder()
        builder.where_like("age", "%name%")
        query_sql = builder.to_sql()
        expected_sql = (
            "SELECT * FROM `users` WHERE `users`.`age` LIKE '%name%'"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_where_not_like_as_operator(self):
        builder = self.get_builder()
        builder.where("age", "not like", "%name%")
        query_sql = builder.to_sql()
        expected_sql = (
            "SELECT * FROM `users` WHERE `users`.`age` NOT LIKE '%name%'"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_where_not_like(self):
        builder = self.get_builder()
        builder.where_not_like("age", "%name%")
        query_sql = builder.to_sql()
        expected_sql = (
            "SELECT * FROM `users` WHERE `users`.`age` NOT LIKE '%name%'"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_where_null(self):
        builder = self.get_builder()
        builder.where_null("name")
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`name` IS NULL"
        self.assertEqual(query_sql, expected_sql)

    def test_where_not_null(self):
        builder = self.get_builder()
        builder.where_not_null("name")
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`name` IS NOT NULL"
        self.assertEqual(query_sql, expected_sql)

    def test_where_not_in(self):
        builder = self.get_builder()
        builder.where_not_in("id", [1, 2, 3])
        query_sql = builder.to_sql()
        expected_sql = (
            "SELECT * FROM `users` WHERE `users`.`id` NOT IN ('1','2','3')"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_where_in(self):
        builder = self.get_builder()
        builder.where_in("id", [1, 2, 3])
        query_sql = builder.to_sql()
        expected_sql = (
            "SELECT * FROM `users` WHERE `users`.`id` IN ('1','2','3')"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_where_lt(self):
        builder = self.get_builder()
        builder.where("age", "<", "20")
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`age` < '20'"
        self.assertEqual(query_sql, expected_sql)

    def test_where_lte(self):
        builder = self.get_builder()
        builder.where("age", "<=", "20")
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`age` <= '20'"
        self.assertEqual(query_sql, expected_sql)

    def test_where_gt(self):
        builder = self.get_builder()
        builder.where("age", ">", "20")
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`age` > '20'"
        self.assertEqual(query_sql, expected_sql)

    def test_where_gte(self):
        builder = self.get_builder()
        builder.where("age", ">=", "20")
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`age` >= '20'"
        self.assertEqual(query_sql, expected_sql)

    def test_where_ne(self):
        builder = self.get_builder()
        builder.where("age", "!=", "20")
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`age` != '20'"
        self.assertEqual(query_sql, expected_sql)

    def test_or_where(self):
        builder = self.get_builder()
        builder.where("age", "20").or_where("age", "<", 20)
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`age` = '20' OR `users`.`age` < '20'"
        self.assertEqual(query_sql, expected_sql)

    def test_where_column(self):
        builder = self.get_builder()
        builder.where_column("name", "username")
        query_sql = builder.to_sql()
        expected_sql = (
            "SELECT * FROM `users` WHERE `users`.`name` = `users`.`username`"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_between(self):
        builder = self.get_builder()
        builder.between("id", 2, 5)
        query_sql = builder.to_sql()
        expected_sql = (
            "SELECT * FROM `users` WHERE `users`.`id` BETWEEN '2' AND '5'"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_not_between(self):
        builder = self.get_builder()
        builder.not_between("id", 2, 5)
        query_sql = builder.to_sql()
        expected_sql = (
            "SELECT * FROM `users` WHERE `users`.`id` NOT BETWEEN '2' AND '5'"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_having(self):
        builder = self.get_builder(table="payments")
        builder.select("user_id").avg("salary").group_by("user_id").having(
            "salary", ">=", "1000"
        )
        query_sql = builder.to_sql()
        expected_sql = (
            "SELECT `payments`.`user_id`, AVG(`payments`.`salary`) AS salary"
            " FROM `payments` GROUP BY `payments`.`user_id` HAVING `payments`.`salary` >= '1000'"
        )
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # LIMIT / OFFSET
    # ------------------------------------------------------------------

    def test_limit(self):
        builder = self.get_builder()
        builder.limit(5)
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` LIMIT 5"
        self.assertEqual(query_sql, expected_sql)

    def test_offset(self):
        builder = self.get_builder()
        builder.offset(5)
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` OFFSET 5"
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # ORDER BY / GROUP BY
    # ------------------------------------------------------------------

    def test_order_by_asc(self):
        builder = self.get_builder()
        builder.order_by("email", "asc")
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` ORDER BY `email` ASC"
        self.assertEqual(query_sql, expected_sql)

    def test_order_by_desc(self):
        builder = self.get_builder()
        builder.order_by("email", "desc")
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` ORDER BY `email` DESC"
        self.assertEqual(query_sql, expected_sql)

    def test_latest(self):
        builder = self.get_builder()
        builder.latest("email")
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` ORDER BY `email` DESC"
        self.assertEqual(query_sql, expected_sql)

    def test_oldest(self):
        builder = self.get_builder()
        builder.oldest("email")
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` ORDER BY `email` ASC"
        self.assertEqual(query_sql, expected_sql)

    def test_group_by(self):
        builder = self.get_builder(table="payments")
        builder.select("user_id").min("salary").group_by("user_id")
        query_sql = builder.to_sql()
        expected_sql = (
            "SELECT `payments`.`user_id`, MIN(`payments`.`salary`) AS salary"
            " FROM `payments` GROUP BY `payments`.`user_id`"
        )
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # JOINs
    # ------------------------------------------------------------------

    def test_join(self):
        builder = self.get_builder()
        builder.join("profiles", "users.id", "=", "profiles.user_id")
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` INNER JOIN `profiles` ON `users`.`id` = `profiles`.`user_id`"
        self.assertEqual(query_sql, expected_sql)

    def test_left_join(self):
        builder = self.get_builder()
        builder.left_join("profiles", "users.id", "=", "profiles.user_id")
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` LEFT JOIN `profiles` ON `users`.`id` = `profiles`.`user_id`"
        self.assertEqual(query_sql, expected_sql)

    def test_right_join(self):
        builder = self.get_builder()
        builder.right_join("profiles", "users.id", "=", "profiles.user_id")
        query_sql = builder.to_sql()
        expected_sql = "SELECT * FROM `users` RIGHT JOIN `profiles` ON `users`.`id` = `profiles`.`user_id`"
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # DML
    # ------------------------------------------------------------------

    def test_create(self):
        builder = self.get_builder().without_global_scopes()
        builder.create(
            {"name": "Corentin All", "email": "corentin@yopmail.com"},
            query=True,
        )
        query_sql = builder.to_sql()
        expected_sql = "INSERT INTO `users` (`users`.`name`, `users`.`email`) VALUES ('Corentin All', 'corentin@yopmail.com')"
        self.assertEqual(query_sql, expected_sql)

    def test_delete(self):
        builder = self.get_builder()
        builder.delete("name", "Joe", query=True)
        query_sql = builder.to_sql()
        expected_sql = "DELETE FROM `users` WHERE `users`.`name` = 'Joe'"
        self.assertEqual(query_sql, expected_sql)

    def test_update(self):
        builder = self.get_builder().update(
            {"name": "Joe", "email": "joe@yopmail.com"}, dry=True
        )
        query_sql = builder.to_sql()
        expected_sql = "UPDATE `users` SET `users`.`name` = 'Joe', `users`.`email` = 'joe@yopmail.com'"
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # TRUNCATE
    # ------------------------------------------------------------------

    def test_truncate(self):
        builder = self.get_builder(dry=True)
        query_sql = builder.truncate()
        expected_sql = "TRUNCATE TABLE `users`"
        self.assertEqual(query_sql, expected_sql)

    def test_truncate_without_foreign_keys(self):
        builder = self.get_builder(dry=True)
        query_sql = builder.truncate(foreign_keys=True)
        expected_sql = [
            "SET FOREIGN_KEY_CHECKS=0",
            "TRUNCATE TABLE `users`",
            "SET FOREIGN_KEY_CHECKS=1",
        ]
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # Locking
    # ------------------------------------------------------------------

    def test_shared_lock(self):
        builder = self.get_builder(dry=True)
        query_sql = builder.where("votes", ">=", 100).shared_lock().to_sql()
        expected_sql = "SELECT * FROM `users` WHERE `users`.`votes` >= '100' LOCK IN SHARE MODE"
        self.assertEqual(query_sql, expected_sql)

    def test_update_lock(self):
        builder = self.get_builder(dry=True)
        query_sql = (
            builder.where("votes", ">=", 100).lock_for_update().to_sql()
        )
        expected_sql = (
            "SELECT * FROM `users` WHERE `users`.`votes` >= '100' FOR UPDATE"
        )
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    def test_builder_alone(self):
        self.assertTrue(
            QueryBuilder(
                dry=True,
                connection_details={
                    "default": "mysql",
                    "mysql": {
                        "driver": "mysql",
                        "host": "localhost",
                        "username": "root",
                        "password": "",
                        "database": "orm",
                        "port": "3306",
                        "prefix": "",
                        "grammar": "mysql",
                        "options": {"charset": "utf8mb4"},
                    },
                },
            ).table("users")
        )

    def test_can_call_with_multi_tables(self):
        builder = self.get_builder()
        query_sql = (
            builder.table("information_schema.columns")
            .select("table_name")
            .where("table_name", "users")
            .to_sql()
        )
        expected_sql = (
            "SELECT `information_schema`.`columns`.`table_name` FROM `information_schema`.`columns`"
            " WHERE `information_schema`.`columns`.`table_name` = 'users'"
        )
        self.assertEqual(query_sql, expected_sql)
