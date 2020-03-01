from src.masonite.orm.grammar.mysql_grammar import MySQLGrammar 
from src.masonite.orm.grammar.GrammarFactory import GrammarFactory
from src.masonite.orm.builder.QueryBuilder import QueryBuilder
import unittest
import inspect

class BaseTestCaseSelectGrammer:

    def setUp(self):
        self.builder = QueryBuilder(GrammarFactory.make(self.grammar), table='users')

    def test_can_compile_select(self):
        to_sql = self.builder.to_sql()

        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_columns(self):
        to_sql = self.builder.select('username', 'password').to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)


    def test_can_compile_with_where(self):
        to_sql = self.builder.select('username', 'password').where('id', 1).to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_or_where(self):
        to_sql = self.builder.where('name', 2).or_where('name', 3).to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_grouped_where(self):
        to_sql = self.builder.where(lambda query: query.where('age', 2).where('name', 'Joe')).to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)


    def test_can_compile_with_several_where(self):
        to_sql = self.builder.select('username', 'password').where('id', 1).where('username', 'joe').to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_several_where_and_limit(self):
        to_sql = self.builder.select('username', 'password').where('id', 1).where('username', 'joe').limit(10).to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_sum(self):
        to_sql = self.builder.sum('age').to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_max(self):
        to_sql = self.builder.max('age').to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_max_and_columns(self):
        to_sql = self.builder.select('username').max('age').to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_max_and_columns_different_order(self):
        to_sql = self.builder.max('age').select('username').to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_order_by(self):
        to_sql = self.builder.select('username').order_by('age', 'desc').to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_group_by(self):
        to_sql = self.builder.select('username').group_by('age').to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_where_in(self):
        to_sql = self.builder.select('username').where_in('age', [1,2,3]).to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_where_null(self):
        to_sql = self.builder.select('username').where_null('age').to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_where_not_null(self):
        to_sql = self.builder.select('username').where_not_null('age').to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_count(self):
        to_sql = self.builder.count().to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_count_column(self):
        to_sql = self.builder.count('money').to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_where_column(self):
        to_sql = self.builder.where_column('name', 'email').to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_where_raw(self):
        to_sql = self.builder.where_raw("`age` = '18'").to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_select_raw(self):
        to_sql = self.builder.select_raw("COUNT(*)").to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_select_raw_with_select(self):
        to_sql = self.builder.select('id').select_raw("COUNT(*)").to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_sub_select(self):
        to_sql = self.builder.where_in('name', 
            self.builder.new().select('age')
        ).to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_complex_sub_select(self):
        to_sql = self.builder.where_in('name', 
            (self.builder.new()
                .select('age').where_in('email', 
                    self.builder.new().select('email')
            ))
        ).to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_sub_select_value(self):
        to_sql = self.builder.where('name', 
            self.builder.new().sum('age')
        ).to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_exists(self):
        to_sql = self.builder.select('age').where_exists(
            self.builder.new().select('username').where('age', 12)
        ).to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_having(self):
        to_sql = self.builder.sum('age').group_by('age').having('age').to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_having_with_expression(self):
        to_sql = self.builder.sum('age').group_by('age').having('age', 10).to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_having_with_greater_than_expression(self):
        to_sql = self.builder.sum('age').group_by('age').having('age', '>', 10).to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_join(self):
        to_sql = self.builder.join('contacts', 'users.id', '=', 'contacts.user_id').to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_left_join(self):
        to_sql = self.builder.left_join('contacts', 'users.id', '=', 'contacts.user_id').to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_multiple_join(self):
        to_sql = self.builder.join('contacts', 'users.id', '=', 'contacts.user_id').join('posts', 'comments.post_id', '=', 'posts.id').to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

    def test_can_compile_limit_and_offset(self):
        to_sql = self.builder.limit(10).offset(10).to_sql()
        sql = getattr(self, inspect.currentframe().f_code.co_name.replace('test_', ''))()
        self.assertEqual(to_sql, sql)

class TestMySQLGrammar(BaseTestCaseSelectGrammer, unittest.TestCase):

    grammar = 'mysql'

    def can_compile_select(self):
        """
        self.builder.to_sql()
        """        
        return "SELECT * FROM `users`"

    def can_compile_with_columns(self):
        """
        self.builder.select('username', 'password').to_sql()
        """
        return "SELECT `username`, `password` FROM `users`"

    def can_compile_with_where(self):
        """
        self.builder.select('username', 'password').where('id', 1).to_sql()
        """
        return "SELECT `username`, `password` FROM `users` WHERE `id` = '1'"


    def can_compile_with_several_where(self):
        """
        self.builder.select('username', 'password').where('id', 1).where('username', 'joe').to_sql() 
        """
        return "SELECT `username`, `password` FROM `users` WHERE `id` = '1' AND `username` = 'joe'"

    def can_compile_with_several_where_and_limit(self):
        """
        self.builder.select('username', 'password').where('id', 1).where('username', 'joe').limit(10).to_sql() 
        """
        return "SELECT `username`, `password` FROM `users` WHERE `id` = '1' AND `username` = 'joe' LIMIT 10"

    def can_compile_with_sum(self):
        """
        self.builder.sum('age').to_sql() 
        """
        return "SELECT SUM(`age`) AS age FROM `users`"

    def can_compile_with_max(self):
        """
        self.builder.max('age').to_sql() 
        """
        return "SELECT MAX(`age`) AS age FROM `users`"

    def can_compile_with_max_and_columns(self):
        """
        self.builder.select('username').max('age').to_sql() 
        """
        return "SELECT `username`, MAX(`age`) AS age FROM `users`"

    def can_compile_with_max_and_columns_different_order(self):
        """
        self.builder.max('age').select('username').to_sql() 
        """
        return "SELECT `username`, MAX(`age`) AS age FROM `users`"

    def can_compile_with_order_by(self):
        """
        self.builder.select('username').order_by('age', 'desc').to_sql() 
        """
        return "SELECT `username` FROM `users` ORDER BY `age` DESC"

    def can_compile_with_group_by(self):
        """
        self.builder.select('username').group_by('age').to_sql() 
        """
        return "SELECT `username` FROM `users` GROUP BY `age`"

    def can_compile_where_in(self):
        """
        self.builder.select('username').where_in('age', [1,2,3]).to_sql() 
        """
        return "SELECT `username` FROM `users` WHERE `age` IN ('1','2','3')"


    def can_compile_where_null(self):
        """
        self.builder.select('username').where_null('age').to_sql() 
        """
        return "SELECT `username` FROM `users` WHERE `age` IS NULL"

    def can_compile_where_not_null(self):
        """
        self.builder.select('username').where_not_null('age').to_sql() 
        """
        return "SELECT `username` FROM `users` WHERE `age` IS NOT NULL"

    def can_compile_where_raw(self):
        """
        self.builder.where_raw("`age` = '18'").to_sql()
        """
        return "SELECT * FROM `users` WHERE `age` = '18'"

    def can_compile_select_raw(self):
        """
        self.builder.select_raw("COUNT(*)").to_sql()
        """
        return "SELECT COUNT(*) FROM `users`"

    def can_compile_limit_and_offset(self):
        """
        self.builder.select_raw("COUNT(*)").to_sql()
        """
        return "SELECT * FROM `users` LIMIT 10 OFFSET 10"

    def can_compile_select_raw_with_select(self):
        """
        self.builder.select('id').select_raw("COUNT(*)").to_sql()
        """
        return "SELECT `id`, COUNT(*) FROM `users`"


    def can_compile_count(self):
        """
        self.builder.count().to_sql() 
        """

        return "SELECT COUNT(*) FROM `users`"

    def can_compile_count_column(self):
        """
        self.builder.count().to_sql() 
        """

        return "SELECT COUNT(`money`) AS money FROM `users`"

    def can_compile_where_column(self):
        """
        self.builder.where_column('name', 'email').to_sql() 
        """

        return "SELECT * FROM `users` WHERE `name` = `email`"


    def can_compile_or_where(self):
        """
        self.builder.where('name', 2).or_where('name', 3).to_sql()
        """
        return "SELECT * FROM `users` WHERE `name` = '2' OR `name` = '3'"

    def can_grouped_where(self):
        """
        self.builder.where(lambda query: query.where('age', 2).where('name', 'Joe')).to_sql()
        """
        return "SELECT * FROM `users` WHERE ( `age` = '2' AND `name` = 'Joe')"

    def can_compile_sub_select(self):
        """
        self.builder.where_in('name', 
            QueryBuilder(GrammarFactory.make(self.grammar), table='users').select('age')
        ).to_sql()
        """

        return "SELECT * FROM `users` WHERE `name` IN (SELECT `age` FROM `users`)"

    def can_compile_sub_select_value(self):
        """
        self.builder.where('name', 
            self.builder.new().sum('age')
        ).to_sql()
        """

        return "SELECT * FROM `users` WHERE `name` = (SELECT SUM(`age`) AS age FROM `users`)"

    def can_compile_complex_sub_select(self):
        """
        self.builder.where_in('name', 
            (QueryBuilder(GrammarFactory.make(self.grammar), table='users')
                .select('age').where_in('email', 
                    QueryBuilder(GrammarFactory.make(self.grammar), table='users').select('email')
            ))
        ).to_sql()
        """
        return "SELECT * FROM `users` WHERE `name` IN (SELECT `age` FROM `users` WHERE `email` IN (SELECT `email` FROM `users`))"

    def can_compile_exists(self):
        """
        self.builder.select('age').where_exists(
            self.builder.new().select('username').where('age', 12)
        ).to_sql()
        """
        return "SELECT `age` FROM `users` WHERE EXISTS (SELECT `username` FROM `users` WHERE `age` = '12')"

    def can_compile_having(self):
        """
        builder.sum('age').group_by('age').having('age').to_sql()
        """
        return "SELECT SUM(`age`) AS age FROM `users` GROUP BY `age` HAVING `age`"

    def can_compile_having_with_expression(self):
        """
        builder.sum('age').group_by('age').having('age', 10).to_sql()
        """
        return "SELECT SUM(`age`) AS age FROM `users` GROUP BY `age` HAVING `age` = '10'"

    def can_compile_having_with_greater_than_expression(self):
        """
        builder.sum('age').group_by('age').having('age', '>', 10).to_sql()
        """
        return "SELECT SUM(`age`) AS age FROM `users` GROUP BY `age` HAVING `age` > '10'"


    def can_compile_join(self):
        """
        builder.join('contacts', 'users.id', '=', 'contacts.user_id').to_sql()
        """
        return "SELECT * FROM `users` INNER JOIN `contacts` ON `users`.`id` = `contacts`.`user_id`"

    def can_compile_left_join(self):
        """
        builder.join('contacts', 'users.id', '=', 'contacts.user_id').to_sql()
        """
        return "SELECT * FROM `users` LEFT JOIN `contacts` ON `users`.`id` = `contacts`.`user_id`"

    def can_compile_multiple_join(self):
        """
        builder.join('contacts', 'users.id', '=', 'contacts.user_id').to_sql()
        """
        return "SELECT * FROM `users` INNER JOIN `contacts` ON `users`.`id` = `contacts`.`user_id` INNER JOIN `posts` ON `comments`.`post_id` = `posts`.`id`"
