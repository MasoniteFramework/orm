from src.masonite.orm.connections.ConnectionFactory import ConnectionFactory
from src.masonite.orm.blueprint.Blueprint import Blueprint


class Schema:

    _connection = ConnectionFactory().make("default")
    _grammer = None
    _default_string_length = "255"

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

        return Blueprint(
            cls._connection.get_grammer(),
            table=table,
            action="create",
            default_string_length=cls._default_string_length,
        )

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
        return Blueprint(
            cls._connection.get_grammer(),
            table=table,
            action="alter",
            default_string_length=cls._default_string_length,
        )

    @classmethod
    def has_column(cls, table, column, query_only=False):
        """Checks if the a table has a specific column

        Arguments:
            table {string} -- The name of a table like 'users'

        Returns:
            masonite.orm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """
        grammar = cls._connection.get_grammer()(table=table)
        query = grammar.column_exists(column).to_sql()
        if query_only:
            return query
        return bool(cls._connection().make_connection().query(query, ()))

    @classmethod
    def set_default_string_length(cls, length):
        cls._default_string_length = length
        return cls

    @classmethod
    def drop_table(cls, table, query_only=True):
        grammar = cls._connection.get_grammer()(table=table)
        query = grammar.drop_table(table).to_sql()
        if query_only:
            return query
        return bool(cls._connection().make_connection().query(query, ()))

    @classmethod
    def drop_table_if_exists(cls, table, exists=False, query_only=True):
        grammar = cls._connection.get_grammer()(table=table)
        query = grammar.drop_table_if_exists(table).to_sql()
        if query_only:
            return query
        return bool(cls._connection().make_connection().query(query, ()))
