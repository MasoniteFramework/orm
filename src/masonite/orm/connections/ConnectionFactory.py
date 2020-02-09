from .MySQLConnection import MySQLConnection
from .SQLiteConnection import SQLiteConnection
from config.database import CONNECTIONS


class ConnectionFactory:

    _connections = {
        "mysql": MySQLConnection,
        "mssql": "",
        "postgres": "",
        "sqlite": SQLiteConnection,
        "oracle": "",
    }

    _connection_settings = {}

    _default = "mysql"

    def register(self, key, connection):
        pass

    def make(self, key):
        if key == "default":
            connection = self._connections.get(self._default)
        else:
            connection = self._connections.get(key)

        if connection:
            connection.set_connections(CONNECTIONS)
            return connection

        raise Exception(
            "The '{connection}' connection does not exist".format(connection=connection)
        )
