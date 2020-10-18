from src.masoniteorm.query.grammars import MSSQLGrammar
from src.masoniteorm.query import QueryBuilder
import unittest


class TestMSSQLUpdateGrammar(unittest.TestCase):
    def setUp(self):
        self.builder = QueryBuilder(MSSQLGrammar, table="users")

    def test_can_compile_update(self):

        to_sql = (
            self.builder.where("name", "bob").update({"name": "Joe"}, dry=True).to_sql()
        )

        sql = "UPDATE [users] SET [users].[name] = 'Joe' WHERE [users].[name] = 'bob'"
        self.assertEqual(to_sql, sql)

    def test_can_compile_update_with_multiple_where(self):
        to_sql = (
            self.builder.where("name", "bob")
            .where("age", 20)
            .update({"name": "Joe"}, dry=True)
            .to_sql()
        )

        sql = "UPDATE [users] SET [users].[name] = 'Joe' WHERE [users].[name] = 'bob' AND [users].[age] = '20'"
        self.assertEqual(to_sql, sql)
