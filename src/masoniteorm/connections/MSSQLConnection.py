from ..exceptions import DriverNotFound, QueryException
from ..query.grammars import MSSQLGrammar
from ..query.processors import MSSQLPostProcessor
from ..schema.platforms import MSSQLPlatform
from .BaseConnection import BaseConnection

CONNECTION_POOL = []

# Options that are handled explicitly when building the connection string.
# Anything in self.options that is NOT in this set will be appended verbatim
# as additional "Key=Value" pairs in the pyodbc connection string.
_MSSQL_KNOWN_OPTIONS = frozenset(
    {
        "driver",
        "integrated_security",
        "connection_timeout",
        "authentication",
        "instance",
        "trusted_connection",
    }
)


class MSSQLConnection(BaseConnection):
    """MSSQL Connection class."""

    name = "mssql"

    def __init__(
        self,
        host=None,
        database=None,
        user=None,
        port=None,
        password=None,
        prefix=None,
        options=None,
        full_details=None,
        name=None,
    ):
        self.host = host
        self.port = int(port) if port else None
        self.database = database
        self.user = user
        self.password = password
        self.prefix = prefix
        self.full_details = full_details or {}
        self.options = options or {}
        self._cursor = None
        self.transaction_level = 0
        self.open = 0
        if name:
            self.name = name

    def _build_connection_string(self):
        """Build the pyodbc connection string from self.options.

        Known options are mapped to their canonical ODBC connection string
        keys. Any remaining entries in self.options that are not in
        ``_MSSQL_KNOWN_OPTIONS`` are appended verbatim as ``Key=Value`` pairs,
        allowing arbitrary ODBC attributes to be passed through.

        Returns:
            str: A semicolon-delimited ODBC connection string.
        """
        driver = self.options.get("driver", "ODBC Driver 17 for SQL Server")
        connection_timeout = str(self.options.get("connection_timeout", "30"))
        integrated_security = self.options.get("integrated_security")
        trusted_connection = self.options.get("trusted_connection")
        authentication = self.options.get("authentication")
        instance = self.options.get("instance", "")

        if instance:
            instance = "\\" + instance

        parts = [
            f"DRIVER={driver}",
            f"SERVER={self.host}{instance},{self.port}",
            f"Connection Timeout={connection_timeout}",
            f"DATABASE={self.database}",
            f"UID={self.user}",
            f"PWD={self.password}",
        ]

        if integrated_security:
            parts.append(f"Integrated Security={integrated_security}")
        if trusted_connection:
            parts.append(f"Trusted_Connection={trusted_connection}")
        if authentication:
            parts.append(f"Authentication={authentication}")

        # Append any extra options not handled above.
        for key, value in self.options.items():
            if key not in _MSSQL_KNOWN_OPTIONS:
                parts.append(f"{key}={value}")

        return ";".join(parts)

    def make_connection(self):
        """This sets the connection on the connection class"""
        try:
            import pyodbc
        except ModuleNotFoundError:
            raise DriverNotFound(
                "You must have the 'pyodbc' package installed to make a connection to Microsoft SQL Server. Please install it using 'pip install pyodbc'"
            )

        if self.has_global_connection():
            return self.get_global_connection()

        self._connection = pyodbc.connect(
            self._build_connection_string(),
            autocommit=True,
        )

        self.enable_disable_foreign_keys()

        self.open = 1
        return self

    def get_database_name(self):
        return self.database

    @classmethod
    def get_default_query_grammar(cls):
        return MSSQLGrammar

    @classmethod
    def get_default_platform(cls):
        return MSSQLPlatform

    @classmethod
    def get_default_post_processor(cls):
        return MSSQLPostProcessor

    def reconnect(self):
        pass

    def commit(self):
        """Transaction"""
        if self.get_transaction_level() == 1:
            self._connection.commit()
            self._connection.autocommit = True

        self.transaction_level -= 1

    def begin(self):
        """MSSQL Transaction"""
        self._connection.autocommit = False
        self.transaction_level += 1
        return self

    def rollback(self):
        """Transaction"""
        if self.get_transaction_level() == 1:
            self._connection.rollback()
            self._connection.autocommit = True

        self.transaction_level -= 1

    def get_transaction_level(self):
        """Transaction"""
        return self.transaction_level

    def get_cursor(self):
        return self._cursor

    def query(self, query, bindings=(), results="*"):
        """Make the actual query that will reach the database and come back with a result.

        Arguments:
            query {string} -- A string query. This could be a qmarked string or a regular query.
            bindings {tuple} -- A tuple of bindings

        Keyword Arguments:
            results {str|1} -- If the results is equal to an asterisks it will call 'fetchAll'
                    else it will return 'fetchOne' and return a single record. (default: {"*"})

        Returns:
            dict|None -- Returns a dictionary of results or None
        """
        try:
            if not self.open:
                self.make_connection()
            self._cursor = self._connection.cursor()
            with self._cursor as cursor:
                if isinstance(query, list) and not self._dry:
                    for q in query:
                        self.statement(q, ())
                    return
                self.statement(query, bindings)
                if results == 1:
                    if not cursor.description:
                        return {}
                    columnNames = [column[0] for column in cursor.description]
                    result = cursor.fetchone()
                    return (
                        dict(zip(columnNames, result))
                        if result is not None
                        else {}
                    )
                else:
                    if not cursor.description:
                        return {}
                    return self.format_cursor_results(cursor.fetchall())

                return {}
        except Exception as e:
            raise QueryException(str(e)) from e
        finally:
            if self.get_transaction_level() <= 0:
                self._connection.close()

    def format_cursor_results(self, cursor_result):
        columnNames = [column[0] for column in self.get_cursor().description]
        results = []
        for record in cursor_result:
            results.append(dict(zip(columnNames, record)))

        return results
