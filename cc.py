"""Sandbox experimental file used to quickly feature test features of the package"""

import inspect

from src.masoniteorm.connections import MySQLConnection, PostgresConnection
from src.masoniteorm.models import Model
from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.query.grammars import MySQLGrammar, PostgresGrammar
from src.masoniteorm.relationships import belongs_to, has_many

# builder = QueryBuilder(connection=PostgresConnection, grammar=PostgresGrammar).table("users").on("postgres")


# print(builder.where("id", 1).or_where(lambda q: q.where('id', 2).or_where('id', 3)).get())


class Logo(Model):
    __connection__ = "t"
    __table__ = "logos"
    __dates__ = ["created_at", "updated_at"]

    @belongs_to("id", "article_id")
    def article(self):
        return Article

    @belongs_to("user_id", "id")
    def user(self):
        return User


class Article(Model):
    __connection__ = "t"
    __table__ = "articles"
    __dates__ = ["created_at", "updated_at"]

    @has_many("id", "article_id")
    def logos(self):
        return Logo

    @belongs_to("user_id", "id")
    def user(self):
        return User


class User(Model):
    __connection__ = "t"
    __table__ = "users"
    __dates__ = ["verified_at"]

    @has_many("id", "user_id")
    def articles(self):
        return Article


class Company(Model):
    __connection__ = "sqlite"


# /Users/personal/programming/masonite/packages/orm/src/masoniteorm/query/QueryBuilder.py

# user = User.create({"name": "phill", "email": "phill"})
# print(inspect.isclass(User))
user = User.with_("articles.logos.user").first()
# user.update({"verified_at": None, "updated_at": None})
# print(user.articles)

print(user.serialize())
# print(User.first())
