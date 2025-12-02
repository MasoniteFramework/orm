from ..config import load_config
from .ConnectionResolver import ConnectionResolver


class ConnectionFactory:
    """Class for controlling the registration and creation of connection types."""

    _connections = {}

    def __init__(self, config_path=None, resolver=None):
        self.config_path = config_path
        self._resolver: ConnectionResolver = resolver

    @classmethod
    def register(cls, key, connection):
        """Registers new connections

        Arguments:
            key {key} -- The key or driver name you want assigned to this connection
            connection {masoniteorm.connections.BaseConnection} -- An instance of a BaseConnection class.

        Returns:
            cls
        """
        cls._connections.update({key: connection})
        return cls

    def make(self, key):
        """Makes already registered connections

        Arguments:
            key {string} -- The name of the connection you want to make

        Raises:
            Exception: Raises exception if there are no driver keys that match

        Returns:
            masoniteorm.connection.BaseConnection -- Returns an instance of a BaseConnection class.
        """
        if not self._resolver:
            self._resolver = load_config(config_path=self.config_path).DB

        connections = self._resolver.get_connection_details()
        if key == "default":
            connection_details = connections.get(connections.get("default"))
            connection = self._connections.get(
                connection_details.get("driver")
            )
        else:
            connection = self._connections.get(key)

        if connection:
            return connection

        raise Exception(
            "The '{connection}' connection does not exist".format(
                connection=key
            )
        )
