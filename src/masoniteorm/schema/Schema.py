from ..connections.ConnectionFactory import ConnectionFactory

from .Blueprint import Blueprint
from .Table import Table
from .TableDiff import TableDiff
from ..exceptions import ConnectionNotRegistered


class Schema:

    _default_string_length = "255"

    def __init__(
        self,
        dry=False,
        connection="default",
        connection_class=None,
        platform=None,
        grammar=None,
        connection_details=None,
        connection_driver=None,
    ):
        self._dry = dry
        self.connection = connection
        self.connection_class = connection_class
        self._connection = None
        self.grammar = grammar
        self.platform = platform
        self.connection_details = connection_details or {}
        self._blueprint = None
        self._sql = None

        if not self.connection_class:
            self.on(self.connection)

        if not self.platform:
            self.platform = self.connection_class.get_default_platform()

    def on(self, connection_key):
        """Change the connection from the default connection

        Arguments:
            connection {string} -- A connection string like 'mysql' or 'mssql'.
                It will be made with the connection factory.

        Returns:
            cls
        """
        from config.database import DB

        if connection_key == "default":
            self.connection = self.connection_details.get("default")

        connection_detail = self._connection_driver = self.connection_details.get(
            self.connection
        )

        if connection_detail:
            self._connection_driver = connection_detail.get("driver")
        else:
            raise ConnectionNotRegistered(
                f"Could not find the '{connection_key}' connection details"
            )

        self.connection_class = DB.connection_factory.make(self._connection_driver)

        return self

    def dry(self):
        """Whether the query should be executed. (default: {False})

        Returns:
            self
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

        self._blueprint = Blueprint(
            self.grammar,
            connection=self.new_connection(),
            table=Table(table),
            action="create",
            platform=self.platform,
            default_string_length=self._default_string_length,
            dry=self._dry,
        )

        return self._blueprint

    def table(self, table):
        """Sets the table and returns the blueprint.

        This should be used as a context manager.

        Arguments:
            table {string} -- The name of a table like 'users'

        Returns:
            masonite.orm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """
        self._table = table

        self._blueprint = Blueprint(
            self.grammar,
            connection=self.new_connection(),
            table=TableDiff(table),
            action="alter",
            platform=self.platform,
            default_string_length=self._default_string_length,
            dry=self._dry,
        )

        return self._blueprint

    def get_connection_information(self):
        return {
            "host": self.connection_details.get(self.connection, {}).get("host"),
            "database": self.connection_details.get(self.connection, {}).get(
                "database"
            ),
            "user": self.connection_details.get(self.connection, {}).get("user"),
            "port": self.connection_details.get(self.connection, {}).get("port"),
            "password": self.connection_details.get(self.connection, {}).get(
                "password"
            ),
            "prefix": self.connection_details.get(self.connection, {}).get("prefix"),
            "options": self.connection_details.get(self.connection, {}).get(
                "options", {}
            ),
            "full_details": self.connection_details.get(self.connection),
        }

    def new_connection(self):
        if self._dry:
            return

        self._connection = self.connection_class(
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
        sql = self.platform().compile_column_exists(table, column)

        if self._dry:
            self._sql = sql
            return sql

        return bool(self.new_connection().query(sql, ()))

    @classmethod
    def set_default_string_length(cls, length):
        cls._default_string_length = length
        return cls

    def drop_table(self, table, query_only=False):
        sql = self.platform().compile_drop_table(table)

        if self._dry:
            self._sql = sql
            return sql

        return bool(self.new_connection().query(sql, ()))

    def drop(self, *args, **kwargs):
        return self.drop_table(*args, **kwargs)

    def drop_table_if_exists(self, table, exists=False, query_only=False):
        sql = self.platform().compile_drop_table_if_exists(table)

        if self._dry:
            self._sql = sql
            return sql

        return bool(self.new_connection().query(sql, ()))

    def rename(self, table, new_name):
        sql = self.platform().compile_rename_table(table, new_name)

        if self._dry:
            self._sql = sql
            return sql

        return bool(self.new_connection().query(sql, ()))

    def truncate(self, table, foreign_keys=False):
        sql = self.platform().compile_truncate(table, foreign_keys=foreign_keys)

        if self._dry:
            self._sql = sql
            return sql

        return bool(self.new_connection().query(sql, ()))

    def has_table(self, table, query_only=False):
        """Checks if the a database has a specific table
        Arguments:
            table {string} -- The name of a table like 'users'
        Returns:
            masonite.orm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """
        sql = self.platform().compile_table_exists(
            table, database=self.get_connection_information().get("database")
        )

        if self._dry:
            self._sql = sql
            return sql

        return bool(self.new_connection().query(sql, ()))

    def enable_foreign_key_constraints(self):
        sql = self.platform().enable_foreign_key_constraints()

        if self._dry:
            self._sql = sql
            return sql

        return bool(self.new_connection().query(sql, ()))

    def disable_foreign_key_constraints(self):
        sql = self.platform().disable_foreign_key_constraints()

        if self._dry:
            self._sql = sql
            return sql

        return bool(self.new_connection().query(sql, ()))
