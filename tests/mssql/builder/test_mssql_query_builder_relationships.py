import inspect
import unittest

from src.masoniteorm.connections import ConnectionFactory
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import MSSQLGrammar
from src.masoniteorm.relationships import belongs_to
from tests.utils import MockConnectionFactory

from dotenv import load_dotenv

load_dotenv(".env")


class Logo(Model):
    __connection__ = "mssql"


class Article(Model):
    __connection__ = "mssql"

    @belongs_to("id", "article_id")
    def logo(self):
        return Logo


class Profile(Model):
    __connection__ = "mssql"


class User(Model):
    __connection__ = "mssql"

    @belongs_to("id", "user_id")
    def articles(self):
        return Article

    @belongs_to("id", "user_id")
    def profile(self):
        return Profile

    @belongs_to("id", "parent_dynamic_id")
    def parent_dynamic(self):
        return self.__class__

    @belongs_to("id", "parent_specified_id")
    def parent_specified(self):
        return User


class BaseTestQueryRelationships(unittest.TestCase):
    maxDiff = None

    def get_builder(self, table="users"):
        connection = MockConnectionFactory().make("mssql")
        return QueryBuilder(
            grammar=MSSQLGrammar,
            connection_class=connection,
            connection="mssql",
            table=table,
            model=User,
        )

    def test_has(self):
        builder = self.get_builder()
        sql = builder.has("articles").to_sql()
        self.assertEqual(
            sql,
            """SELECT * FROM [users] WHERE EXISTS ("""
            """SELECT * FROM [articles] WHERE [articles].[user_id] = [users].[id]"""
            """)""",
        )

    def test_has_reference_to_self(self):
        builder = self.get_builder()
        sql = builder.has("parent_dynamic").to_sql()
        self.assertEqual(
            sql,
            """SELECT * FROM [users] WHERE EXISTS ("""
            """SELECT * FROM [users] WHERE [users].[parent_dynamic_id] = [users].[id]"""
            """)""",
        )

    def test_has_reference_to_self_using_class(self):
        builder = self.get_builder()
        sql = builder.has("parent_specified").to_sql()
        self.assertEqual(
            sql,
            """SELECT * FROM [users] WHERE EXISTS ("""
            """SELECT * FROM [users] WHERE [users].[parent_specified_id] = [users].[id]"""
            """)""",
        )

    def test_where_has_query(self):
        builder = self.get_builder()
        sql = builder.where_has("articles", lambda q: q.where("active", 1)).to_sql()
        self.assertEqual(
            sql,
            """SELECT * FROM [users] WHERE EXISTS ("""
            """SELECT * FROM [articles] WHERE [articles].[user_id] = [users].[id] AND [articles].[active] = '1'"""
            """)""",
        )

    def test_relationship_multiple_has(self):
        to_sql = User.has("articles", "profile").to_sql()
        self.assertEqual(
            to_sql,
            """SELECT * FROM [users] WHERE EXISTS ("""
            """SELECT * FROM [articles] WHERE [articles].[user_id] = [users].[id]"""
            """) AND EXISTS ("""
            """SELECT * FROM [profiles] WHERE [profiles].[user_id] = [users].[id]"""
            """)""",
        )

    def test_relationship_multiple_has_calls(self):
        to_sql = User.has("articles").has("profile").to_sql()
        self.assertEqual(
            to_sql,
            """SELECT * FROM [users] WHERE EXISTS ("""
            """SELECT * FROM [articles] WHERE [articles].[user_id] = [users].[id]"""
            """) AND EXISTS ("""
            """SELECT * FROM [profiles] WHERE [profiles].[user_id] = [users].[id]"""
            """)""",
        )

    def test_nested_has(self):
        to_sql = User.has("articles.logo").to_sql()
        self.assertEqual(
            to_sql,
            """SELECT * FROM [users] WHERE EXISTS (SELECT * FROM [articles] WHERE [articles].[user_id] = [users].[id] AND EXISTS (SELECT * FROM [logos] WHERE [logos].[article_id] = [articles].[id]))""",
        )
