from .Blueprint import Blueprint
from .Table import Table
from .TableDiff import TableDiff
from ..exceptions import ConnectionNotRegistered
from ..config import load_config


class Schema:

    _default_string_length = "255"
    _type_hints_map = {
        "string": str,
        "char": str,
        "big_increments": int,
        "integer": int,
        "big_integer": int,
        "tiny_integer": int,
        "small_integer": int,
        "medium_integer": int,
        "integer_unsigned": int,
        "big_integer_unsigned": int,
        "tiny_integer_unsigned": int,
        "small_integer_unsigned": int,
        "medium_integer_unsigned": int,
        "increments": int,
        "uuid": str,
        "binary": bytes,
        "boolean": bool,
        "decimal": float,
        "double": float,
        "enum": str,
        "text": str,
        "float": float,
        "geometry": str,  # ?
        "json": dict,
        "jsonb": bytes,
        "inet": str,
        "cidr": str,
        "macaddr": str,
        "long_text": str,
        "point": str,  # ?
        "time": str,  # or pendulum.DateTime
        "timestamp": str,  # or pendulum.DateTime
        "date": str,  # or pendulum.DateTime
        "year": str,
        "datetime": str,  # or pendulum.DateTime
        "tiny_increments": int,
        "unsigned": int,
        "unsigned_integer": int,
    }

    def __init__(
        self,
        dry=False,
        connection="default",
        connection_class=None,
        platform=None,
        grammar=None,
        connection_details=None,
        schema=None,
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
        self.schema = schema

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
        DB = load_config().DB

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
            masoniteorm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """
        self._table = table

        self._blueprint = Blueprint(
            self.grammar,
            connection=self.new_connection(),
            table=Table(table),
            action="create",
            platform=self.platform,
            schema=self.schema,
            default_string_length=self._default_string_length,
            dry=self._dry,
        )

        return self._blueprint

    def create_table_if_not_exists(self, table):
        self._table = table

        self._blueprint = Blueprint(
            self.grammar,
            connection=self.new_connection(),
            table=Table(table),
            action="create_table_if_not_exists",
            platform=self.platform,
            schema=self.schema,
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
            masoniteorm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """
        self._table = table

        self._blueprint = Blueprint(
            self.grammar,
            connection=self.new_connection(),
            table=TableDiff(table),
            action="alter",
            platform=self.platform,
            schema=self.schema,
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

        self._connection = (
            self.connection_class(**self.get_connection_information())
            .set_schema(self.schema)
            .make_connection()
        )

        return self._connection

    def has_column(self, table, column, query_only=False):
        """Checks if the a table has a specific column

        Arguments:
            table {string} -- The name of a table like 'users'

        Returns:
            masoniteorm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """
        sql = self.platform().compile_column_exists(table, column)

        if self._dry:
            self._sql = sql
            return sql

        return bool(self.new_connection().query(sql, ()))

    def get_columns(self, table, dict=True):
        table = self.platform().get_current_schema(
            self.new_connection(), table, schema=self.get_schema()
        )
        result = {}
        if dict:
            for column in table.get_added_columns().items():
                result.update({column[0]: column[1]})
            return result
        else:
            return table.get_added_columns().items()

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

    def get_schema(self):
        """Gets the schema set on the migration class"""
        return self.schema or self.get_connection_information().get("full_details").get(
            "schema"
        )

    def has_table(self, table, query_only=False):
        """Checks if the a database has a specific table
        Arguments:
            table {string} -- The name of a table like 'users'
        Returns:
            masoniteorm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """
        sql = self.platform().compile_table_exists(
            table,
            database=self.get_connection_information().get("database"),
            schema=self.get_schema(),
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
