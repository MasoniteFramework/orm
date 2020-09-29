from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.connections import MySQLConnection, PostgresConnection
from src.masoniteorm.query.grammars import MySQLGrammar, PostgresGrammar
from config.database import DATABASES
from src.masoniteorm.models import Model


builder = QueryBuilder(connection=PostgresConnection, grammar=PostgresGrammar, connection_details=DATABASES).table("users").on("postgres")



# print(builder.where("id", 1).or_where(lambda q: q.where('id', 2).or_where('id', 3)).get())

class User(Model):
    __connection__ = "sqlite"
    __table__ = "users"

# user = User.create({"name": "phill", "email": "phill"})
print(User.get().count())

print(user.serialize())
# print(User.first())