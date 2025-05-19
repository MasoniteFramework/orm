"""Sandbox experimental file used to quickly feature test features of the package
"""

from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.connections import MySQLConnection, PostgresConnection
from src.masoniteorm.query.grammars import MySQLGrammar, PostgresGrammar
from src.masoniteorm.models import Model
from src.masoniteorm.relationships import has_many
import inspect


# builder = QueryBuilder(connection=PostgresConnection, grammar=PostgresGrammar).table("users").on("postgres")



# print(builder.where("id", 1).or_where(lambda q: q.where('id', 2).or_where('id', 3)).get())

class User(Model):
    __connection__ = "mysql"
    __table__ = "users"
    __dates__ = ["verified_at"]

    @has_many("id", "user_id")
    def articles(self):
        return Article
class Article(Model):
    __connection__ = "sqlite"


# user = User.create({"name": "phill", "email": "phill"})
# print(inspect.isclass(User))
user = User.first()
user.update({"verified_at": None, "updated_at": None})
print(user.first().serialize())

# print(user.serialize())
# print(User.first())