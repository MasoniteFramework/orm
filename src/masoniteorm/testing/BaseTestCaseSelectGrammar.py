import inspect

from ..query import QueryBuilder
from ..expressions import JoinClause
from ..models import Model


class MockConnection:

    connection_details = {}

    def make_connection(self):
        return self


class BaseTestCaseSelectGrammar:
    def setUp(self):
        self.builder = QueryBuilder(
            self.grammar,
            table="users",
            connection_class=MockConnection,
            model=Model(),
            dry=True,
        )

    def test_can_compile_select(self):
        to_sql = self.builder.to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_order_by_and_first(self):
        to_sql = self.builder.order_by("id", "asc").first(query=True).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_columns(self):
        to_sql = self.builder.select("username", "password").to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_where(self):
        to_sql = self.builder.select("username", "password").where("id", 1).to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_or_where(self):
        to_sql = self.builder.where("name", 2).or_where("name", 3).to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_grouped_where(self):
        to_sql = self.builder.where(
            lambda query: query.where("age", 2).where("name", "Joe")
        ).to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_several_where(self):
        to_sql = (
            self.builder.select("username", "password")
            .where("id", 1)
            .where("username", "joe")
            .to_sql()
        )
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_several_where_and_limit(self):
        to_sql = (
            self.builder.select("username", "password")
            .where("id", 1)
            .where("username", "joe")
            .limit(10)
            .to_sql()
        )
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_sum(self):
        to_sql = self.builder.sum("age").to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_max(self):
        to_sql = self.builder.max("age").to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_max_and_columns(self):
        to_sql = self.builder.select("username").max("age").to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_max_and_columns_different_order(self):
        to_sql = self.builder.max("age").select("username").to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_order_by(self):
        to_sql = self.builder.select("username").order_by("age", "desc").to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_multiple_order_by(self):
        to_sql = (
            self.builder.select("username")
            .order_by("age", "desc")
            .order_by("name")
            .to_sql()
        )
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_with_group_by(self):
        to_sql = self.builder.select("username").group_by("age").to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_where_in(self):
        to_sql = self.builder.select("username").where_in("age", [1, 2, 3]).to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_where_in_empty(self):
        to_sql = self.builder.where_in("age", []).to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_where_not_in(self):
        to_sql = self.builder.select("username").where_not_in("age", [1, 2, 3]).to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_where_null(self):
        to_sql = self.builder.select("username").where_null("age").to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_where_not_null(self):
        to_sql = self.builder.select("username").where_not_null("age").to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_count(self):
        to_sql = self.builder.count("*").to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_count_column(self):
        to_sql = self.builder.count("money").to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_where_column(self):
        to_sql = self.builder.where_column("name", "email").to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_sub_select(self):
        to_sql = self.builder.where_in(
            "name", self.builder.new().select("age")
        ).to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_complex_sub_select(self):
        to_sql = self.builder.where_in(
            "name",
            (
                self.builder.new()
                .select("age")
                .where_in("email", self.builder.new().select("email"))
            ),
        ).to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_sub_select_where(self):
        to_sql = self.builder.where_in(
            "age", self.builder.new().select("age").where("age", 2).where("name", "Joe")
        ).to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_sub_select_value(self):
        to_sql = self.builder.where("name", self.builder.new().sum("age")).to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_exists(self):
        to_sql = (
            self.builder.select("age")
            .where_exists(self.builder.new().select("username").where("age", 12))
            .to_sql()
        )
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_not_exists(self):
        to_sql = (
            self.builder.select("age")
            .where_not_exists(self.builder.new().select("username").where("age", 12))
            .to_sql()
        )
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_having(self):
        to_sql = self.builder.sum("age").group_by("age").having("age").to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_having_with_expression(self):
        to_sql = self.builder.sum("age").group_by("age").having("age", 10).to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_having_with_greater_than_expression(self):
        to_sql = self.builder.sum("age").group_by("age").having("age", ">", 10).to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_join(self):
        to_sql = self.builder.join(
            "contacts", "users.id", "=", "contacts.user_id"
        ).to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_join_clause(self):
        clause = (
            JoinClause("report_groups as rg")
            .on("bgt.fund", "=", "rg.fund")
            .on("bgt.dept", "=", "rg.dept")
            .on("bgt.acct", "=", "rg.acct")
            .on("bgt.sub", "=", "rg.sub")
        )
        to_sql = self.builder.join(clause).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_join_clause_with_value(self):
        clause = (
            JoinClause("report_groups as rg")
            .on_value("bgt.active", "=", "1")
            .or_on_value("bgt.acct", "=", "1234")
        )
        to_sql = self.builder.join(clause).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_join_clause_with_null(self):
        clause = (
            JoinClause("report_groups as rg")
            .on_null("bgt.acct")
            .or_on_not_null("bgt.dept")
        )
        to_sql = self.builder.join(clause).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_join_clause_with_lambda(self):
        to_sql = self.builder.join(
            "report_groups as rg",
            lambda clause: (clause.on("bgt.fund", "=", "rg.fund").on_null("bgt")),
        ).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_left_join_clause_with_lambda(self):
        to_sql = self.builder.left_join(
            "report_groups as rg",
            lambda clause: (clause.on("bgt.fund", "=", "rg.fund").or_on_null("bgt")),
        ).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_right_join_clause_with_lambda(self):
        to_sql = self.builder.right_join(
            "report_groups as rg",
            lambda clause: (clause.on("bgt.fund", "=", "rg.fund").or_on_null("bgt")),
        ).to_sql()

        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_left_join(self):
        to_sql = self.builder.left_join(
            "contacts", "users.id", "=", "contacts.user_id"
        ).to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_multiple_join(self):
        to_sql = (
            self.builder.join("contacts", "users.id", "=", "contacts.user_id")
            .join("posts", "comments.post_id", "=", "posts.id")
            .to_sql()
        )
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_limit_and_offset(self):
        to_sql = self.builder.limit(10).offset(10).to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_between(self):
        to_sql = self.builder.between("age", 18, 21).to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_not_between(self):
        to_sql = self.builder.not_between("age", 18, 21).to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_user_where_raw_and_where(self):
        to_sql = (
            self.builder.where_raw("age = '18'").where("name", "=", "James").to_sql()
        )
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_can_compile_first_or_fail(self):
        to_sql = (
            self.builder.where("is_admin", "=", True).first_or_fail(query=True).to_sql()
        )
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_where_like(self):
        to_sql = self.builder.where("age", "like", "%name%").to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_where_not_like(self):
        to_sql = self.builder.where("age", "not like", "%name%").to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_shared_lock(self):
        to_sql = self.builder.where("votes", ">=", 100).shared_lock().to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)

    def test_update_lock(self):
        to_sql = self.builder.where("votes", ">=", 100).lock_for_update().to_sql()
        sql = getattr(
            self, inspect.currentframe().f_code.co_name.replace("test_", "")
        )()
        self.assertEqual(to_sql, sql)
