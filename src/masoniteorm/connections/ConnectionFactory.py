from .ConnectionResolver import ConnectionResolver

from .MySQLConnection import MySQLConnection
from .SQLiteConnection import SQLiteConnection
from .PostgresConnection import PostgresConnection


class ConnectionFactory:
    """Class for controlling the registration and creation of connection types."""

    _connections = {
        "mysql": MySQLConnection,
        "mssql": "",
        "postgres": PostgresConnection,
        "sqlite": SQLiteConnection,
        "oracle": "",
    }

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

        connections = ConnectionResolver.get_connection_details()

        if key == "default":
            connection_details = connections.get(connections.get("default"))
            connection = self._connections.get(connection_details.get("driver"))
        else:
            connection_details = connections.get(key)
            connection = self._connections.get(connection_details.get("driver"))

        if connection:
            return connection

        raise Exception(
            "The '{connection}' connection does not exist".format(connection=connection)
        )
