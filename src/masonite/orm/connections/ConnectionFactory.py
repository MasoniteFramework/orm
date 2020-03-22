from config.database import CONNECTIONS

from .MySQLConnection import MySQLConnection
from .SQLiteConnection import SQLiteConnection


class ConnectionFactory:
    """Class for controlling the registration and creation of connection types.
    """

    _connections = {
        "mysql": MySQLConnection,
        "mssql": "",
        "postgres": "",
        "sqlite": SQLiteConnection,
        "oracle": "",
    }

    _connection_settings = {}

    _default = "mysql"

    @classmethod
    def register(cls, key, connection):
        """Registers new connections

        Arguments:
            key {key} -- The key or driver name you want assigned to this connection
            connection {masonite.orm.connections.BaseConnection} -- An instance of a BaseConnection class.

        Returns:
            cls
        """
        cls.update({key: connection})
        return cls

    def make(self, key):
        """Makes already registered connections

        Arguments:
            key {string} -- The name of the connection you want to make

        Raises:
            Exception: Raises exception if there are no driver keys that match

        Returns:
            masonite.orm.connection.BaseConnection -- Returns an instance of a BaseConnection class.
        """
        if key == "default":
            connection = self._connections.get(self._default)
            connection.set_connection_settings(CONNECTIONS.get(self._default))
        else:
            connection = self._connections.get(key)
            connection.set_connection_settings(CONNECTIONS.get(key))

        if connection:
            return connection

        raise Exception(
            "The '{connection}' connection does not exist".format(connection=connection)
        )
