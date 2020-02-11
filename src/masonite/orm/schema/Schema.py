from src.masonite.orm.connections.ConnectionFactory import ConnectionFactory
from src.masonite.orm.blueprint.Blueprint import Blueprint


class Schema:

    _connection = ConnectionFactory().make("default")
    _grammer = None

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

        return Blueprint(cls._connection.get_grammer(), table=table, action="create")

    @classmethod
    def table(cls, table):
        """Sets the table and returns the blueprint.

        This should be used as a context manager.

        Arguments:
            table {string} -- The name of a table like 'users'

        Returns:
            masonite.orm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """
        cls._table = table
        return Blueprint(cls._connection.get_grammer(), table=table, action="alter")

    @classmethod
    def has_column(cls, table, column):
        """Checks if the a table has a specific column

        Arguments:
            table {string} -- The name of a table like 'users'

        Returns:
            masonite.orm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """

        cls._table = table
        self._grammer = cls._connection.get_grammer()(table=table)
        query = cls.has_column_query(table, column)
        return bool(cls._connection().make_connection().query(query, grammar._bindings))

    @classmethod
    def has_column_query(cls, table, column):
        """Sets the table and returns the blueprint.

        This should be used as a context manager.

        Arguments:
            table {string} -- The name of a table like 'users'

        Returns:
            masonite.orm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """
        grammar = cls._grammer or cls._connection.get_grammer()(table=table)
        return grammar.column_exists(column).to_sql()
