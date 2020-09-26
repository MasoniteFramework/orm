from src.masoniteorm.orm.query import QueryBuilder
from src.masoniteorm.orm.connections import MySQLConnection, PostgresConnection
from src.masoniteorm.orm.query.grammars import MySQLGrammar, PostgresGrammar
from config.database import DATABASES
from src.masoniteorm.orm.models import Model


builder = QueryBuilder(connection=PostgresConnection, grammar=PostgresGrammar, connection_details=DATABASES).table("users").on("postgres")



# print(builder.where("id", 1).or_where(lambda q: q.where('id', 2).or_where('id', 3)).get())

class User(Model):
    __connection__ = "postgres"
    __table__ = """public"."users"""

user = User.create({"name": "phill", "email": "phill"})
print(User.get().serialize())

print(user.serialize())
# print(User.first())