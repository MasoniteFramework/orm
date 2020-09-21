from src.masoniteorm.orm.query import QueryBuilder
from src.masoniteorm.orm.connections import MySQLConnection
from src.masoniteorm.orm.query.grammars import MySQLGrammar
from config.database import DATABASES
from src.masoniteorm.orm.models import Model


builder = QueryBuilder(connection=MySQLConnection, grammar=MySQLGrammar, connection_details=DATABASES).table("users")



# print(builder.where("id", 1).or_where(lambda q: q.where('id', 2).or_where('id', 3)).get())

class User(Model):
    pass

print(User.all().count())
print(User.where("id", 1).get().count())
print(User.first())