from src.masonite.orm.connections.ConnectionFactory import ConnectionFactory
from src.masonite.orm.blueprint.Blueprint import Blueprint


class Schema:

    _connection = ConnectionFactory().make("default")

    @classmethod
    def on(cls, connection):
        """Change the connection from the default connection

        Arguments:
            connection {string} -- A connection string like 'mysql' or 'mssql'.
                It will be made with the connection factory.

        Returns:
            cls
        """
        cls._connection = ConnectionFactory().make(connection)
        return cls

    @classmethod
    def create(cls, table):
        """Sets the table and returns the blueprint.

        This should be used as a context manager.

        Arguments:
            table {string} -- The name of a table like 'users'

        Returns:
            masonite.orm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """
        cls._table = table
        return Blueprint(cls._connection.get_grammer(), table=table)
