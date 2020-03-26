import inspect
import unittest

from src.masonite.orm.builder import QueryBuilder
from src.masonite.orm.grammar import MySQLGrammar
from src.masonite.orm.models import Model
from tests.utils import MockConnectionFactory


class BaseTestQueryBuilder:
    def get_builder(self, table="users"):
        connection = MockConnectionFactory().make("default")
        return QueryBuilder(
            self.grammar,
            connection,
            table=table,
            owner=Model
        )

    def test_sum(self):
        builder = self.get_builder()
        builder.sum('age')

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_max(self):
        builder = self.get_builder()
        builder.max('age')

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_min(self):
        builder = self.get_builder()
        builder.min('age')

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_avg(self):
        builder = self.get_builder()
        builder.avg('age')
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

    # def test_first(self):
    #     builder = self.get_builder()
    #     builder.first()
    #     sql = getattr(
    #         self, inspect.currentframe().f_code.co_name.replace("test_", "")
    #     )()
    #     self.assertEqual(builder.to_sql(), sql)

    def test_select(self):
        builder = self.get_builder()
        builder.select('name', 'email')
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_select_raw(self):
        builder = self.get_builder()
        builder.select_raw('count(email) as email_count')
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_create(self):
        builder = self.get_builder()
        builder.create({"name": "Corentin All", 'email': 'corentin@yopmail.com'})
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_delete(self):
        builder = self.get_builder()
        builder.delete("name", "Joe")
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_where(self):
        builder = self.get_builder()
        builder.where('name', 'Joe')
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_where_exists(self):
        builder = self.get_builder()
        builder.where_exists('name')
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

    # def test_update(self):
    #     builder = self.get_builder()
    #     builder.update({"name": "Joe", "email": "joe@yopmail.com"})
    #     sql = getattr(
    #         self, inspect.currentframe().f_code.co_name.replace("test_", "")
    #     )()
    #     self.assertEqual(builder.to_sql(), sql)

    def test_increment(self):
        builder = self.get_builder()
        builder.increment('age', 1)
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_decrement(self):
        builder = self.get_builder()
        builder.decrement('age', 1)
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_count(self):
        builder = self.get_builder()
        builder.count('id')
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_order_by_asc(self):
        builder = self.get_builder()
        builder.order_by('email', 'asc')
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)

    def test_order_by_desc(self):
        builder = self.get_builder()
        builder.order_by('email', 'desc')
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(builder.to_sql(), sql)


class MySQLQueryBuilderTest(BaseTestQueryBuilder, unittest.TestCase):
    grammar = MySQLGrammar

    def sum(self):
        """
            builder = self.get_builder()
            builder.sum('age')
        """
        return 'SELECT SUM(`age`) AS age FROM `users`'

    def max(self):
        """
            builder = self.get_builder()
            builder.max('age')
        """
        return "SELECT MAX(`age`) AS age FROM `users`"

    def min(self):
        """
            builder = self.get_builder()
            builder.min('age')
        """
        return "SELECT MIN(`age`) AS age FROM `users`"

    def avg(self):
        """
            builder = self.get_builder()
            builder.avg('age')
        """
        return "SELECT AVG(`age`) AS age FROM `users`"

    def first(self):
        """
            builder = self.get_builder()
            builder.first()
        """
        return "SELECT * FROM `users` LIMIT 1"

    def all(self):
        """
            builder = self.get_builder()
            builder.all()
        """
        return "SELECT * FROM `users`"

    def get(self):
        """
            builder = self.get_builder()
            builder.get()
        """
        return "SELECT * FROM `users`"

    def select(self):
        """
            builder = self.get_builder()
            builder.select('name', 'email')
        """
        return "SELECT `name`, `email` FROM `users`"

    def select_raw(self):
        """
            builder = self.get_builder()
            builder.select_raw('count(email) as email_count')
        """
        return 'SELECT count(email) as email_count FROM `users`'

    def create(self):
        """
            builder = get_builder()
            builder.create({"name": "Corentin All", 'email': 'corentin@yopmail.com'})
        """
        return "INSERT INTO `users` (`name`, `email`) VALUES ('Corentin All', 'corentin@yopmail.com')"

    def delete(self):
        """
            builder = get_builder()
            builder.delete("name', 'Joe')
        """
        return "DELETE FROM `users` WHERE `name` = 'Joe'"

    def where(self):
        """
            builder = get_builder()
            builder.where('name', 'Joe')
        """
        return "SELECT * FROM `users` WHERE `name` = 'Joe'"

    def where_exists(self):
        """
            builder = get_builder()
            builder.where_exists('name')
        """
        return "SELECT * FROM `users` WHERE EXISTS 'name'"

    def limit(self):
        """
            builder = get_builder()
            builder.limit(5)
        """
        return "SELECT * FROM `users` LIMIT 5"

    def offset(self):
        """
            builder = get_builder()
            builder.offset(5)
        """
        return "SELECT * FROM `users` OFFSET 5"

    def join(self):
        """
            builder.join("profiles", "users.id", "=", "profiles.user_id")
        """
        return "SELECT * FROM `users` INNER JOIN `profiles` ON `users`.`id` = `profiles`.`user_id`"

    def left_join(self):
        """
            builder.left_join("profiles", "users.id", "=", "profiles.user_id")
        """
        return "SELECT * FROM `users` LEFT JOIN `profiles` ON `users`.`id` = `profiles`.`user_id`"

    def right_join(self):
        """
            builder.right_join("profiles", "users.id", "=", "profiles.user_id")
        """
        return "SELECT * FROM `users` RIGHT JOIN `profiles` ON `users`.`id` = `profiles`.`user_id`"

    def update(self):
        """
            builder.update({"name": "Joe", "email": "joe@yopmail.com"})
        """
        return "UPDATE `users` SET `name` = 'Joe', `email` = 'joe@yopmail.com'"

    def increment(self):
        """
            builder.increment('age', 1)
        """
        return "UPDATE `users` SET `age` = `age` + '1'"

    def decrement(self):
        """
            builder.decrement('age', 1)
        """
        return "UPDATE `users` SET `age` = `age` - '1'"

    def count(self):
        """
            builder.count(id)
        """
        return 'SELECT COUNT(`id`) AS id FROM `users`'

    def order_by_asc(self):
        """
            builder.order_by('email', 'asc')
        """
        return 'SELECT * FROM `users` ORDER BY `email` ASC'

    def order_by_desc(self):
        """
            builder.order_by('email', 'des')
        """
        return 'SELECT * FROM `users` ORDER BY `email` DESC'

