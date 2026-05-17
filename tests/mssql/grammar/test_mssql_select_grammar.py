import unittest

from src.masoniteorm.expressions import JoinClause
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import MSSQLGrammar


class MockConnection:
    connection_details = {}

    def make_connection(self):
        return self


class TestMSSQLSelectGrammar(unittest.TestCase):
    """Tests for SQL SELECT compilation with the MSSQL grammar.

    Each test is self-contained: it builds a query and asserts the expected
    SQL string inline, with no separate data-provider class.
    """

    maxDiff = None

    def setUp(self):
        self.builder = QueryBuilder(
            MSSQLGrammar,
            table="users",
            connection_class=MockConnection,
            model=Model(),
            dry=True,
        )

    # ------------------------------------------------------------------
    # Basic SELECT
    # ------------------------------------------------------------------

    def test_can_compile_select(self):
        query_sql = self.builder.to_sql()
        expected_sql = "SELECT * FROM [users]"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_with_columns(self):
        query_sql = self.builder.select("username", "password").to_sql()
        expected_sql = (
            "SELECT [users].[username], [users].[password] FROM [users]"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_select_raw(self):
        query_sql = self.builder.select_raw("COUNT(*)").to_sql()
        expected_sql = "SELECT COUNT(*) FROM [users]"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_select_raw_with_select(self):
        query_sql = self.builder.select("id").select_raw("COUNT(*)").to_sql()
        expected_sql = "SELECT [users].[id], COUNT(*) FROM [users]"
        self.assertEqual(query_sql, expected_sql)

    def test_select_distinct(self):
        query_sql = self.builder.select("group").distinct().to_sql()
        expected_sql = "SELECT DISTINCT [users].[group] FROM [users]"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_count(self):
        query_sql = self.builder.count("*").to_sql()
        expected_sql = "SELECT COUNT(*) AS m_count_reserved FROM [users]"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_count_column(self):
        query_sql = self.builder.count("money").to_sql()
        expected_sql = "SELECT COUNT([users].[money]) AS money FROM [users]"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_with_sum(self):
        query_sql = self.builder.sum("age").to_sql()
        expected_sql = "SELECT SUM([users].[age]) AS age FROM [users]"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_with_max(self):
        query_sql = self.builder.max("age").to_sql()
        expected_sql = "SELECT MAX([users].[age]) AS age FROM [users]"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_with_max_and_columns(self):
        query_sql = self.builder.select("username").max("age").to_sql()
        expected_sql = (
            "SELECT [users].[username], MAX([users].[age]) AS age FROM [users]"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_with_max_and_columns_different_order(self):
        query_sql = self.builder.max("age").select("username").to_sql()
        expected_sql = (
            "SELECT [users].[username], MAX([users].[age]) AS age FROM [users]"
        )
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # ORDER BY / GROUP BY / LIMIT / OFFSET
    # ------------------------------------------------------------------

    def test_can_compile_order_by_and_first(self):
        query_sql = (
            self.builder.order_by("id", "asc").first(query=True).to_sql()
        )
        expected_sql = "SELECT TOP 1 * FROM [users] ORDER BY [id] ASC"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_with_order_by(self):
        query_sql = (
            self.builder.select("username").order_by("age", "desc").to_sql()
        )
        expected_sql = (
            "SELECT [users].[username] FROM [users] ORDER BY [age] DESC"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_with_multiple_order_by(self):
        query_sql = (
            self.builder.select("username")
            .order_by("age", "desc")
            .order_by("name")
            .to_sql()
        )
        expected_sql = "SELECT [users].[username] FROM [users] ORDER BY [age] DESC, [name] ASC"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_with_group_by(self):
        query_sql = self.builder.select("username").group_by("age").to_sql()
        expected_sql = (
            "SELECT [users].[username] FROM [users] GROUP BY [users].[age]"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_limit_and_offset(self):
        query_sql = self.builder.limit(10).offset(10).to_sql()
        expected_sql = (
            "SELECT * FROM [users] OFFSET 10 ROWS FETCH NEXT 10 ROWS ONLY"
        )
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # WHERE clauses
    # ------------------------------------------------------------------

    def test_can_compile_with_where(self):
        query_sql = (
            self.builder.select("username", "password").where("id", 1).to_sql()
        )
        expected_sql = "SELECT [users].[username], [users].[password] FROM [users] WHERE [users].[id] = '1'"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_with_several_where(self):
        query_sql = (
            self.builder.select("username", "password")
            .where("id", 1)
            .where("username", "joe")
            .to_sql()
        )
        expected_sql = (
            "SELECT [users].[username], [users].[password] FROM [users]"
            " WHERE [users].[id] = '1' AND [users].[username] = 'joe'"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_with_several_where_and_limit(self):
        query_sql = (
            self.builder.select("username", "password")
            .where("id", 1)
            .where("username", "joe")
            .limit(10)
            .to_sql()
        )
        expected_sql = (
            "SELECT TOP 10 [users].[username], [users].[password] FROM [users]"
            " WHERE [users].[id] = '1' AND [users].[username] = 'joe'"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_or_where(self):
        query_sql = self.builder.where("name", 2).or_where("name", 3).to_sql()
        expected_sql = "SELECT * FROM [users] WHERE [users].[name] = '2' OR [users].[name] = '3'"
        self.assertEqual(query_sql, expected_sql)

    def test_can_grouped_where(self):
        query_sql = self.builder.where(
            lambda q: q.where("age", 2).where("name", "Joe")
        ).to_sql()
        expected_sql = "SELECT * FROM [users] WHERE ([users].[age] = '2' AND [users].[name] = 'Joe')"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_where_in(self):
        query_sql = (
            self.builder.select("username").where_in("age", [1, 2, 3]).to_sql()
        )
        expected_sql = "SELECT [users].[username] FROM [users] WHERE [users].[age] IN ('1','2','3')"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_where_in_empty(self):
        query_sql = self.builder.where_in("age", []).to_sql()
        expected_sql = "SELECT * FROM [users] WHERE 0 = 1"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_where_not_in(self):
        query_sql = (
            self.builder.select("username")
            .where_not_in("age", [1, 2, 3])
            .to_sql()
        )
        expected_sql = "SELECT [users].[username] FROM [users] WHERE [users].[age] NOT IN ('1','2','3')"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_where_null(self):
        query_sql = self.builder.select("username").where_null("age").to_sql()
        expected_sql = "SELECT [users].[username] FROM [users] WHERE [users].[age] IS NULL"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_where_not_null(self):
        query_sql = (
            self.builder.select("username").where_not_null("age").to_sql()
        )
        expected_sql = "SELECT [users].[username] FROM [users] WHERE [users].[age] IS NOT NULL"
        self.assertEqual(query_sql, expected_sql)

    def test_or_where_null(self):
        query_sql = (
            self.builder.where_null("column1")
            .or_where_null("column2")
            .to_sql()
        )
        expected_sql = "SELECT * FROM [users] WHERE [users].[column1] IS NULL OR [users].[column2] IS NULL"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_where_column(self):
        query_sql = self.builder.where_column("name", "email").to_sql()
        expected_sql = (
            "SELECT * FROM [users] WHERE [users].[name] = [users].[email]"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_where_raw(self):
        query_sql = self.builder.where_raw("[age] = '18'").to_sql()
        expected_sql = "SELECT * FROM [users] WHERE [age] = '18'"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_where_raw_and_where_with_multiple_bindings(self):
        query = self.builder.where_raw(
            "[age] = ? AND [is_admin] = ?", [18, True]
        ).where("email", "test@example.com")
        query_sql = query.to_qmark()
        expected_sql = "SELECT * FROM [users] WHERE [age] = ? AND [is_admin] = ? AND [users].[email] = ?"
        self.assertEqual(query_sql, expected_sql)
        self.assertEqual(query._bindings, [18, True, "test@example.com"])

    def test_can_user_where_raw_and_where(self):
        query_sql = (
            self.builder.where_raw("age = '18'")
            .where("name", "=", "James")
            .to_sql()
        )
        expected_sql = "SELECT * FROM [users] WHERE age = '18' AND [users].[name] = 'James'"
        self.assertEqual(query_sql, expected_sql)

    def test_where_like(self):
        query_sql = self.builder.where("age", "like", "%name%").to_sql()
        expected_sql = (
            "SELECT * FROM [users] WHERE [users].[age] LIKE '%name%'"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_where_not_like(self):
        query_sql = self.builder.where("age", "not like", "%name%").to_sql()
        expected_sql = (
            "SELECT * FROM [users] WHERE [users].[age] NOT LIKE '%name%'"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_where_regexp(self):
        query_sql = self.builder.where("age", "regexp", "Joe").to_sql()
        expected_sql = "SELECT * FROM [users] WHERE [users].[age] LIKE 'Joe'"
        self.assertEqual(query_sql, expected_sql)

    def test_where_not_regexp(self):
        query_sql = self.builder.where("age", "not regexp", "Joe").to_sql()
        expected_sql = (
            "SELECT * FROM [users] WHERE [users].[age] NOT LIKE 'Joe'"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_where_date(self):
        query_sql = self.builder.where_date(
            "created_at", "2022-06-01"
        ).to_sql()
        expected_sql = "SELECT * FROM [users] WHERE DATE([users].[created_at]) = '2022-06-01'"
        self.assertEqual(query_sql, expected_sql)

    def test_where_exists_with_lambda(self):
        query_sql = self.builder.where_exists(
            lambda q: q.where("age", 1)
        ).to_sql()
        expected_sql = "SELECT * FROM [users] WHERE EXISTS (SELECT * FROM [users] WHERE [users].[age] = '1')"
        self.assertEqual(query_sql, expected_sql)

    def test_where_not_exists_with_lambda(self):
        query_sql = self.builder.where_not_exists(
            lambda q: q.where("age", 1)
        ).to_sql()
        expected_sql = "SELECT * FROM [users] WHERE NOT EXISTS (SELECT * FROM [users] WHERE [users].[age] = '1')"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_between(self):
        query_sql = self.builder.between("age", 18, 21).to_sql()
        expected_sql = (
            "SELECT * FROM [users] WHERE [users].[age] BETWEEN '18' AND '21'"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_not_between(self):
        query_sql = self.builder.not_between("age", 18, 21).to_sql()
        expected_sql = "SELECT * FROM [users] WHERE [users].[age] NOT BETWEEN '18' AND '21'"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_first_or_fail(self):
        query_sql = (
            self.builder.where("is_admin", "=", True)
            .first_or_fail(query=True)
            .to_sql()
        )
        expected_sql = (
            "SELECT TOP 1 * FROM [users] WHERE [users].[is_admin] = '1'"
        )
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # HAVING
    # ------------------------------------------------------------------

    def test_can_compile_having(self):
        query_sql = (
            self.builder.sum("age").group_by("age").having("age").to_sql()
        )
        expected_sql = "SELECT SUM([users].[age]) AS age FROM [users] GROUP BY [users].[age] HAVING [users].[age]"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_having_raw(self):
        query_sql = (
            self.builder.select_raw("COUNT(*) as counts")
            .having_raw("counts > 18")
            .to_sql()
        )
        expected_sql = (
            "SELECT COUNT(*) as counts FROM [users] HAVING counts > 18"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_having_raw_with_order(self):
        query_sql = (
            self.builder.select_raw("COUNT(*) as counts")
            .having_raw("counts > 10")
            .order_by_raw("counts DESC")
            .to_sql()
        )
        expected_sql = "SELECT COUNT(*) as counts FROM [users] HAVING counts > 10 ORDER BY counts DESC"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_having_with_expression(self):
        query_sql = (
            self.builder.sum("age").group_by("age").having("age", 10).to_sql()
        )
        expected_sql = "SELECT SUM([users].[age]) AS age FROM [users] GROUP BY [users].[age] HAVING [users].[age] = '10'"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_having_with_greater_than_expression(self):
        query_sql = (
            self.builder.sum("age")
            .group_by("age")
            .having("age", ">", 10)
            .to_sql()
        )
        expected_sql = "SELECT SUM([users].[age]) AS age FROM [users] GROUP BY [users].[age] HAVING [users].[age] > '10'"
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # Locking (MSSQL uses ROWLOCK hints)
    # ------------------------------------------------------------------

    def test_shared_lock(self):
        query_sql = (
            self.builder.where("votes", ">=", 100).shared_lock().to_sql()
        )
        expected_sql = "SELECT * FROM [users] WITH(ROWLOCK) WHERE [users].[votes] >= '100'"
        self.assertEqual(query_sql, expected_sql)

    def test_update_lock(self):
        query_sql = (
            self.builder.where("votes", ">=", 100).lock_for_update().to_sql()
        )
        expected_sql = "SELECT * FROM [users] WITH(ROWLOCK) WHERE [users].[votes] >= '100'"
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # Sub-selects
    # ------------------------------------------------------------------

    def test_can_compile_sub_select(self):
        query_sql = self.builder.where_in(
            "name", self.builder.new().select("age")
        ).to_sql()
        expected_sql = "SELECT * FROM [users] WHERE [users].[name] IN (SELECT [users].[age] FROM [users])"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_sub_select_where(self):
        query_sql = self.builder.where_in(
            "age",
            self.builder.new()
            .select("age")
            .where("age", 2)
            .where("name", "Joe"),
        ).to_sql()
        expected_sql = (
            "SELECT * FROM [users] WHERE [users].[age] IN"
            " (SELECT [users].[age] FROM [users] WHERE [users].[age] = '2' AND [users].[name] = 'Joe')"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_sub_select_from_lambda(self):
        expected = (
            "SELECT * FROM [users] WHERE [users].[age] IN"
            " (SELECT [users].[age] FROM [users] WHERE [users].[age] = '2' AND [users].[name] = 'Joe')"
        )
        query_sql = (
            self.builder.new()
            .where_in(
                "age",
                lambda q: q.select("age").where("age", 2).where("name", "Joe"),
            )
            .to_sql()
        )
        expected_sql = expected
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_sub_select_value(self):
        query_sql = self.builder.where(
            "name", self.builder.new().sum("age")
        ).to_sql()
        expected_sql = "SELECT * FROM [users] WHERE [users].[name] = (SELECT SUM([users].[age]) AS age FROM [users])"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_complex_sub_select(self):
        query_sql = self.builder.where_in(
            "name",
            self.builder.new()
            .select("age")
            .where_in("email", self.builder.new().select("email")),
        ).to_sql()
        expected_sql = (
            "SELECT * FROM [users] WHERE [users].[name] IN"
            " (SELECT [users].[age] FROM [users] WHERE [users].[email] IN"
            " (SELECT [users].[email] FROM [users]))"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_exists(self):
        query_sql = (
            self.builder.select("age")
            .where_exists(
                self.builder.new().select("username").where("age", 12)
            )
            .to_sql()
        )
        expected_sql = (
            "SELECT [users].[age] FROM [users]"
            " WHERE EXISTS (SELECT [users].[username] FROM [users] WHERE [users].[age] = '12')"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_not_exists(self):
        query_sql = (
            self.builder.select("age")
            .where_not_exists(
                self.builder.new().select("username").where("age", 12)
            )
            .to_sql()
        )
        expected_sql = (
            "SELECT [users].[age] FROM [users]"
            " WHERE NOT EXISTS (SELECT [users].[username] FROM [users] WHERE [users].[age] = '12')"
        )
        self.assertEqual(query_sql, expected_sql)

    # ------------------------------------------------------------------
    # JOINs
    # ------------------------------------------------------------------

    def test_can_compile_join(self):
        query_sql = self.builder.join(
            "contacts", "users.id", "=", "contacts.user_id"
        ).to_sql()
        expected_sql = "SELECT * FROM [users] INNER JOIN [contacts] ON [users].[id] = [contacts].[user_id]"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_left_join(self):
        query_sql = self.builder.left_join(
            "contacts", "users.id", "=", "contacts.user_id"
        ).to_sql()
        expected_sql = "SELECT * FROM [users] LEFT JOIN [contacts] ON [users].[id] = [contacts].[user_id]"
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_multiple_join(self):
        query_sql = (
            self.builder.join("contacts", "users.id", "=", "contacts.user_id")
            .join("posts", "comments.post_id", "=", "posts.id")
            .to_sql()
        )
        expected_sql = (
            "SELECT * FROM [users]"
            " INNER JOIN [contacts] ON [users].[id] = [contacts].[user_id]"
            " INNER JOIN [posts] ON [comments].[post_id] = [posts].[id]"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_join_clause(self):
        clause = (
            JoinClause("report_groups as rg")
            .on("bgt.fund", "=", "rg.fund")
            .on("bgt.dept", "=", "rg.dept")
            .on("bgt.acct", "=", "rg.acct")
            .on("bgt.sub", "=", "rg.sub")
        )
        query_sql = self.builder.join(clause).to_sql()
        expected_sql = (
            "SELECT * FROM [users] INNER JOIN [report_groups] AS [rg]"
            " ON [bgt].[fund] = [rg].[fund] AND [bgt].[dept] = [rg].[dept]"
            " AND [bgt].[acct] = [rg].[acct] AND [bgt].[sub] = [rg].[sub]"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_join_clause_with_value(self):
        clause = (
            JoinClause("report_groups as rg")
            .on_value("bgt.active", "=", "1")
            .or_on_value("bgt.acct", "=", "1234")
        )
        query_sql = self.builder.join(clause).to_sql()
        expected_sql = (
            "SELECT * FROM [users] INNER JOIN [report_groups] AS [rg]"
            " ON [bgt].[active] = '1' OR [bgt].[acct] = '1234'"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_join_clause_with_null(self):
        clause = (
            JoinClause("report_groups as rg")
            .on_null("bgt.acct")
            .or_on_null("bgt.dept")
            .on_value("rg.abc", 10)
        )
        query_sql = self.builder.join(clause).to_sql()
        expected_sql = (
            "SELECT * FROM [users] INNER JOIN [report_groups] AS [rg]"
            " ON [acct] IS NULL OR [dept] IS NULL AND [rg].[abc] = '10'"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_join_clause_with_not_null(self):
        clause = (
            JoinClause("report_groups as rg")
            .on_not_null("bgt.acct")
            .or_on_not_null("bgt.dept")
            .on_value("rg.abc", 10)
        )
        query_sql = self.builder.join(clause).to_sql()
        expected_sql = (
            "SELECT * FROM [users] INNER JOIN [report_groups] AS [rg]"
            " ON [acct] IS NOT NULL OR [dept] IS NOT NULL AND [rg].[abc] = '10'"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_join_clause_with_lambda(self):
        query_sql = self.builder.join(
            "report_groups as rg",
            lambda clause: clause.on("bgt.fund", "=", "rg.fund").on_null(
                "bgt"
            ),
        ).to_sql()
        expected_sql = (
            "SELECT * FROM [users] INNER JOIN [report_groups] AS [rg]"
            " ON [bgt].[fund] = [rg].[fund] AND [bgt] IS NULL"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_left_join_clause_with_lambda(self):
        query_sql = self.builder.left_join(
            "report_groups as rg",
            lambda clause: clause.on("bgt.fund", "=", "rg.fund").or_on_null(
                "bgt"
            ),
        ).to_sql()
        expected_sql = (
            "SELECT * FROM [users] LEFT JOIN [report_groups] AS [rg]"
            " ON [bgt].[fund] = [rg].[fund] OR [bgt] IS NULL"
        )
        self.assertEqual(query_sql, expected_sql)

    def test_can_compile_right_join_clause_with_lambda(self):
        query_sql = self.builder.right_join(
            "report_groups as rg",
            lambda clause: clause.on("bgt.fund", "=", "rg.fund").or_on_null(
                "bgt"
            ),
        ).to_sql()
        expected_sql = (
            "SELECT * FROM [users] RIGHT JOIN [report_groups] AS [rg]"
            " ON [bgt].[fund] = [rg].[fund] OR [bgt] IS NULL"
        )
        self.assertEqual(query_sql, expected_sql)
