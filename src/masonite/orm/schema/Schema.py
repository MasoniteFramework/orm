from src.masonite.orm.connections.ConnectionFactory import ConnectionFactory
from src.masonite.orm.blueprint.Blueprint import Blueprint

class Schema:

    _connection = ConnectionFactory().make('default')
    
    @classmethod
    def on(cls, connection):
        cls._connection = ConnectionFactory().make(connection)
        return cls

    @classmethod
    def create(cls, table):
        cls._table = table
        return Blueprint(cls._connection.get_grammer(), table=table)