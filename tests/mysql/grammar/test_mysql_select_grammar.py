import inspect
import unittest

from src.masoniteorm.query.grammars import MySQLGrammar
from src.masoniteorm.testing import BaseTestCaseSelectGrammar


class TestMySQLGrammar(BaseTestCaseSelectGrammar, unittest.TestCase):

    grammar = MySQLGrammar

    def can_compile_select(self):
        """
        self.builder.to_sql()
        """
        return "SELECT * FROM `users`"

    def can_compile_with_columns(self):
        """
        self.builder.select('username', 'password').to_sql()
        """
        return "SELECT `users`.`username`, `users`.`password` FROM `users`"

    def can_compile_order_by_and_first(self):
        """
        self.builder.order_by('id', 'asc').first()
        """
        return """SELECT * FROM `users` ORDER BY `id` ASC LIMIT 1"""

    def can_compile_with_where(self):
        """
        self.builder.select('username', 'password').where('id', 1).to_sql()
        """
        return "SELECT `users`.`username`, `users`.`password` FROM `users` WHERE `users`.`id` = '1'"

    def can_compile_with_several_where(self):
        """
        self.builder.select('username', 'password').where('id', 1).where('username', 'joe').to_sql()
        """
        return "SELECT `users`.`username`, `users`.`password` FROM `users` WHERE `users`.`id` = '1' AND `users`.`username` = 'joe'"

    def can_compile_with_several_where_and_limit(self):
        """
        self.builder.select('username', 'password').where('id', 1).where('username', 'joe').limit(10).to_sql()
        """
        return "SELECT `users`.`username`, `users`.`password` FROM `users` WHERE `users`.`id` = '1' AND `users`.`username` = 'joe' LIMIT 10"

    def can_compile_with_sum(self):
        """
        self.builder.sum('age').to_sql()
        """
        return "SELECT SUM(`users`.`age`) AS age FROM `users`"

    def can_compile_with_max(self):
        """
        self.builder.max('age').to_sql()
        """
        return "SELECT MAX(`users`.`age`) AS age FROM `users`"

    def can_compile_with_max_and_columns(self):
        """
        self.builder.select('username').max('age').to_sql()
        """
        return "SELECT `users`.`username`, MAX(`users`.`age`) AS age FROM `users`"

    def can_compile_with_max_and_columns_different_order(self):
        """
        self.builder.max('age').select('username').to_sql()
        """
        return "SELECT `users`.`username`, MAX(`users`.`age`) AS age FROM `users`"

    def can_compile_with_order_by(self):
        """
        self.builder.select('username').order_by('age', 'desc').to_sql()
        """
        return "SELECT `users`.`username` FROM `users` ORDER BY `age` DESC"

    def can_compile_with_multiple_order_by(self):
        """
        self.builder.select('username').order_by('age', 'desc').order_by('name').to_sql()
        """
        return "SELECT `users`.`username` FROM `users` ORDER BY `age` DESC, `name` ASC"

    def can_compile_with_group_by(self):
        """
        self.builder.select('username').group_by('age').to_sql()
        """
        return "SELECT `users`.`username` FROM `users` GROUP BY `users`.`age`"

    def can_compile_where_in(self):
        """
        self.builder.select('username').where_in('age', [1,2,3]).to_sql()
        """
        return "SELECT `users`.`username` FROM `users` WHERE `users`.`age` IN ('1','2','3')"

    def can_compile_where_in_empty(self):
        """
        self.builder.where_in('age', []).to_sql()
        """
        return """SELECT * FROM `users` WHERE 0 = 1"""

    def can_compile_where_not_in(self):
        """
        self.builder.select('username').where_not_in('age', [1,2,3]).to_sql()
        """
        return "SELECT `users`.`username` FROM `users` WHERE `users`.`age` NOT IN ('1','2','3')"

    def can_compile_where_null(self):
        """
        self.builder.select('username').where_null('age').to_sql()
        """
        return "SELECT `users`.`username` FROM `users` WHERE `users`.`age` IS NULL"

    def can_compile_where_not_null(self):
        """
        self.builder.select('username').where_not_null('age').to_sql()
        """
        return "SELECT `users`.`username` FROM `users` WHERE `users`.`age` IS NOT NULL"

    def can_compile_where_raw(self):
        """
        self.builder.where_raw("`age` = '18'").to_sql()
        """
        return "SELECT * FROM `users` WHERE `users`.`age` = '18'"

    def can_compile_select_raw(self):
        """
        self.builder.select_raw("COUNT(*)").to_sql()
        """
        return "SELECT COUNT(*) FROM `users`"

    def can_compile_limit_and_offset(self):
        """
        self.builder.limit(10).offset(10).to_sql()
        """
        return "SELECT * FROM `users` LIMIT 10 OFFSET 10"

    def can_compile_select_raw_with_select(self):
        """
        self.builder.select('id').select_raw("COUNT(*)").to_sql()
        """
        return "SELECT `users`.`id`, COUNT(*) FROM `users`"

    def can_compile_count(self):
        """
        self.builder.count().to_sql()
        """

        return "SELECT COUNT(*) AS m_count_reserved FROM `users`"

    def can_compile_count_column(self):
        """
        self.builder.count().to_sql()
        """

        return "SELECT COUNT(`users`.`money`) AS money FROM `users`"

    def can_compile_where_column(self):
        """
        self.builder.where_column('name', 'email').to_sql()
        """

        return "SELECT * FROM `users` WHERE `users`.`name` = `users`.`email`"

    def can_compile_or_where(self):
        """
        self.builder.where('name', 2).or_where('name', 3).to_sql()
        """
        return (
            "SELECT * FROM `users` WHERE `users`.`name` = '2' OR `users`.`name` = '3'"
        )

    def can_grouped_where(self):
        """
        self.builder.where(lambda query: query.where('age', 2).where('name', 'Joe')).to_sql()
        """
        return "SELECT * FROM `users` WHERE (`users`.`age` = '2' AND `users`.`name` = 'Joe')"

    def can_compile_sub_select(self):
        """
        self.builder.where_in('name',
            QueryBuilder(GrammarFactory.make(self.grammar), table='users').select('age')
        ).to_sql()
        """

        return "SELECT * FROM `users` WHERE `users`.`name` IN (SELECT `users`.`age` FROM `users`)"

    def can_compile_sub_select_where(self):
        """
        self.builder.where_in('age',
            QueryBuilder(GrammarFactory.make(self.grammar), table='users').select('age').where('age', 2).where('name', 'Joe')
        ).to_sql()
        """

        return "SELECT * FROM `users` WHERE `users`.`age` IN (SELECT `users`.`age` FROM `users` WHERE `users`.`age` = '2' AND `users`.`name` = 'Joe')"

    def can_compile_sub_select_value(self):
        """
        self.builder.where('name',
            self.builder.new().sum('age')
        ).to_sql()
        """

        return "SELECT * FROM `users` WHERE `users`.`name` = (SELECT SUM(`users`.`age`) AS age FROM `users`)"

    def can_compile_complex_sub_select(self):
        """
        self.builder.where_in('name',
            (QueryBuilder(GrammarFactory.make(self.grammar), table='users')
                .select('age').where_in('email',
                    QueryBuilder(GrammarFactory.make(self.grammar), table='users').select('email')
            ))
        ).to_sql()
        """
        return "SELECT * FROM `users` WHERE `users`.`name` IN (SELECT `users`.`age` FROM `users` WHERE `users`.`email` IN (SELECT `users`.`email` FROM `users`))"

    def can_compile_exists(self):
        """
        self.builder.select('age').where_exists(
            self.builder.new().select('username').where('age', 12)
        ).to_sql()
        """
        return "SELECT `users`.`age` FROM `users` WHERE EXISTS (SELECT `users`.`username` FROM `users` WHERE `users`.`age` = '12')"

    def can_compile_not_exists(self):
        """
        self.builder.select('age').where_not_exists(
            self.builder.new().select('username').where('age', 12)
        ).to_sql()
        """
        return "SELECT `users`.`age` FROM `users` WHERE NOT EXISTS (SELECT `users`.`username` FROM `users` WHERE `users`.`age` = '12')"

    def can_compile_having(self):
        """
        builder.sum('age').group_by('age').having('age').to_sql()
        """
        return "SELECT SUM(`users`.`age`) AS age FROM `users` GROUP BY `users`.`age` HAVING `users`.`age`"

    def can_compile_having_with_expression(self):
        """
        builder.sum('age').group_by('age').having('age', 10).to_sql()
        """
        return "SELECT SUM(`users`.`age`) AS age FROM `users` GROUP BY `users`.`age` HAVING `users`.`age` = '10'"

    def can_compile_having_with_greater_than_expression(self):
        """
        builder.sum('age').group_by('age').having('age', '>', 10).to_sql()
        """
        return "SELECT SUM(`users`.`age`) AS age FROM `users` GROUP BY `users`.`age` HAVING `users`.`age` > '10'"

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

    def can_compile_between(self):
        """
        builder.between('age', 18, 21).to_sql()
        """
        return "SELECT * FROM `users` WHERE `users`.`age` BETWEEN '18' AND '21'"

    def can_compile_not_between(self):
        """
        builder.not_between('age', 18, 21).to_sql()
        """
        return "SELECT * FROM `users` WHERE `users`.`age` NOT BETWEEN '18' AND '21'"

    def test_can_compile_where_raw(self):
        to_sql = self.builder.where_raw("`age` = '18'").to_sql()
        self.assertEqual(to_sql, "SELECT * FROM `users` WHERE `age` = '18'")

    def test_can_compile_select_raw(self):
        to_sql = self.builder.select_raw("COUNT(*)").to_sql()
        self.assertEqual(to_sql, "SELECT COUNT(*) FROM `users`")

    def test_can_compile_select_raw_with_select(self):
        to_sql = self.builder.select("id").select_raw("COUNT(*)").to_sql()
        self.assertEqual(to_sql, "SELECT `users`.`id`, COUNT(*) FROM `users`")

    def can_compile_first_or_fail(self):
        """
        builder = self.get_builder()
        builder.where("is_admin", "=", True).first_or_fail()
        """
        return """SELECT * FROM `users` WHERE `users`.`is_admin` = '1' LIMIT 1"""

    def where_not_like(self):
        """
        builder = self.get_builder()
        builder.where("age", "not like", "%name%").to_sql()
        """
        return "SELECT * FROM `users` WHERE `users`.`age` NOT LIKE '%name%'"

    def where_like(self):
        """
        builder = self.get_builder()
        builder.where("age", "like", "%name%").to_sql()
        """
        return "SELECT * FROM `users` WHERE `users`.`age` LIKE '%name%'"

    def can_compile_join_clause(self):
        """
        builder = self.get_builder()
        clause = (
            JoinClause("report_groups as rg")
            .on("bgt.fund", "=", "rg.fund")
            .on_value("bgt.active", "=", "1")
            .or_on_value("bgt.acct", "=", "1234")
        )
        builder.join(clause).to_sql()
        """
        return "SELECT * FROM `users` INNER JOIN `report_groups` AS `rg` ON `bgt`.`fund` = `rg`.`fund` AND `bgt`.`dept` = `rg`.`dept` AND `bgt`.`acct` = `rg`.`acct` AND `bgt`.`sub` = `rg`.`sub`"

    def can_compile_join_clause_with_value(self):
        """
        builder = self.get_builder()
        clause = (
            JoinClause("report_groups as rg")
            .on_value("bgt.active", "=", "1")
            .or_on_value("bgt.acct", "=", "1234")
        )
        builder.join(clause).to_sql()
        """
        return "SELECT * FROM `users` INNER JOIN `report_groups` AS `rg` ON `bgt`.`active` = '1' OR `bgt`.`acct` = '1234'"

    def can_compile_join_clause_with_null(self):
        """
        builder = self.get_builder()
        clause = (
            JoinClause("report_groups as rg")
            .on_null("bgt.acct")
            .or_on_not_null("bgt.dept")
        )
        builder.join(clause).to_sql()
        """
        return "SELECT * FROM `users` INNER JOIN `report_groups` AS `rg` ON `acct` IS NULL OR `dept` IS NOT NULL"

    def can_compile_join_clause_with_lambda(self):
        """
        builder = self.get_builder()
        builder.join(
            "report_groups as rg",
            lambda clause: (
                clause.on("bgt.fund", "=", "rg.fund")
                .on_null("bgt")
            ),
        ).to_sql()
        """
        return "SELECT * FROM `users` INNER JOIN `report_groups` AS `rg` ON `bgt`.`fund` = `rg`.`fund` AND `bgt` IS NULL"

    def can_compile_left_join_clause_with_lambda(self):
        """
        builder = self.get_builder()
        builder.left_join(
            "report_groups as rg",
            lambda clause: (
                clause.on("bgt.fund", "=", "rg.fund")
                .or_on_null("bgt")
            ),
        ).to_sql()
        """
        return "SELECT * FROM `users` LEFT JOIN `report_groups` AS `rg` ON `bgt`.`fund` = `rg`.`fund` OR `bgt` IS NULL"

    def can_compile_right_join_clause_with_lambda(self):
        """
        builder = self.get_builder()
        builder.right_join(
            "report_groups as rg",
            lambda clause: (
                clause.on("bgt.fund", "=", "rg.fund")
                .or_on_null("bgt")
            ),
        ).to_sql()
        """
        return "SELECT * FROM `users` RIGHT JOIN `report_groups` AS `rg` ON `bgt`.`fund` = `rg`.`fund` OR `bgt` IS NULL"

    def shared_lock(self):
        """
        builder = self.get_builder()
        builder.where("age", "not like", "%name%").to_sql()
        """
        return "SELECT * FROM `users` WHERE `users`.`votes` >= '100' LOCK IN SHARE MODE"

    def update_lock(self):
        """
        builder = self.get_builder()
        builder.where("age", "not like", "%name%").to_sql()
        """
        return "SELECT * FROM `users` WHERE `users`.`votes` >= '100' FOR UPDATE"

    def can_user_where_raw_and_where(self):
        """
        builder.where_raw("`age` = '18'").where("name", "=", "James").to_sql()
        """
        return "SELECT * FROM `users` WHERE age = '18' AND `users`.`name` = 'James'"
