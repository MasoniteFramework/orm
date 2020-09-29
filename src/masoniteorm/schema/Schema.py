from ..connections.ConnectionFactory import ConnectionFactory
from .Blueprint import Blueprint


class Schema:

    _default_string_length = "255"

    def __init__(
        self,
        dry=False,
        connection=None,
        grammar=None,
        connection_details={},
        connection_driver=None,
    ):
        self._dry = dry
        self.connection = connection
        self._connection = None
        self.grammar = grammar
        self.connection_details = connection_details
        self._connection_driver = connection_driver

    def on(self, connection):
        """Change the connection from the default connection

        Arguments:
            connection {string} -- A connection string like 'mysql' or 'mssql'.
                It will be made with the connection factory.

        Returns:
            cls
        """
        self.connection = ConnectionFactory().make(connection)

        return self

    def dry(self):
        """Change the connection from the default connection

        Arguments:
            connection {string} -- A connection string like 'mysql' or 'mssql'.
                It will be made with the connection factory.

        Returns:
            cls
        """
        self._dry = True
        return self

    def create(self, table):
        """Sets the table and returns the blueprint.

        This should be used as a context manager.

        Arguments:
            table {string} -- The name of a table like 'users'

        Returns:
            masonite.orm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """
        self._table = table

        return Blueprint(
            self.grammar,
            connection=self.new_connection(),
            table=table,
            action="create",
            default_string_length=self._default_string_length,
            dry=self._dry,
        )

    def table(self, table):
        """Sets the table and returns the blueprint.

        This should be used as a context manager.

        Arguments:
            table {string} -- The name of a table like 'users'

        Returns:
            masonite.orm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """
        self._table = table
        return Blueprint(
            self.grammar,
            connection=self.new_connection(),
            table=table,
            action="alter",
            default_string_length=self._default_string_length,
            dry=self._dry,
        )

    def get_connection_information(self):

        return {
            "host": self.connection_details.get(self._connection_driver, {}).get(
                "host"
            ),
            "database": self.connection_details.get(self._connection_driver, {}).get(
                "database"
            ),
            "user": self.connection_details.get(self._connection_driver, {}).get(
                "user"
            ),
            "port": self.connection_details.get(self._connection_driver, {}).get(
                "port"
            ),
            "password": self.connection_details.get(self._connection_driver, {}).get(
                "password"
            ),
            "prefix": self.connection_details.get(self._connection_driver, {}).get(
                "prefix"
            ),
        }

    def new_connection(self):
        if self._dry:
            return

        self._connection = self.connection(
            **self.get_connection_information()
        ).make_connection()

        return self._connection

    def has_column(self, table, column, query_only=False):
        """Checks if the a table has a specific column

        Arguments:
            table {string} -- The name of a table like 'users'

        Returns:
            masonite.orm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """
        grammar = self.grammar(table=table)
        query = grammar.column_exists(column).to_sql()
        if query_only:
            return query
        return self.new_connection().query(query, ())

    @classmethod
    def set_default_string_length(cls, length):
        cls._default_string_length = length
        return cls

    def drop_table(self, table, query_only=False):
        grammar = self.grammar(table=table)
        query = grammar.drop_table(table).to_sql()
        if query_only:
            return query

        return self.new_connection().make_connection().query(query, ())

    def drop(self, *args, **kwargs):
        return self.drop_table(*args, **kwargs)

    def drop_table_if_exists(self, table, exists=False, query_only=False):
        grammar = self.grammar(table=table)
        query = grammar.drop_table_if_exists(table).to_sql()
        if query_only:
            return query
        self.new_connection().make_connection().query(query, (), results=1)

    def rename(self, table, new_name, query_only=False):
        grammar = self.grammar(table=table)
        query = grammar.rename_table(
            current_table_name=table, new_table_name=new_name
        ).to_sql()
        if query_only:
            return query
        return bool(self.new_connection().query(query, ()))

    def truncate(self, table, query_only=True):
        grammar = self.grammar(table=table)
        query = grammar.truncate_table(table=table).to_sql()
        if query_only:
            return query
        return bool(self.new_connection().query(query, ()))

    def has_table(self, table, query_only=False):
        """Checks if the a database has a specific table
        Arguments:
            table {string} -- The name of a table like 'users'
        Returns:
            masonite.orm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """
        print("checking table exists")
        if self._dry:
            grammar = self.grammar(table=table, database="orm")
        else:
            grammar = self.grammar(
                table=table, database=self.new_connection().get_database_name()
            )

        query = grammar.table_exists().to_sql()
        if query_only:
            return query
        return bool(self.new_connection().make_connection().query(query, ()))
