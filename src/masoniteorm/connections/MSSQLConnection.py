import random

from ..exceptions import DriverNotFound
from .BaseConnection import BaseConnection
from ..query.grammars import MSSQLGrammar
from ..schema.platforms import MSSQLPlatform
from ..query.processors import MSSQLPostProcessor
from ..exceptions import QueryException


CONNECTION_POOL = []


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
        if port:
            self.port = int(port)
        else:
            self.port = port
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

        mssql_driver = self.options.get("driver", "ODBC Driver 17 for SQL Server")

        self._connection = pyodbc.connect(
            f"DRIVER={mssql_driver};SERVER={self.host},{self.port};DATABASE={self.database};UID={self.user};PWD={self.password}",
            autocommit=True,
        )

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
                query = query.replace("'?'", "?")
                self.statement(query, bindings)
                if results == 1:
                    if not cursor.description:
                        return {}
                    columnNames = [column[0] for column in cursor.description]
                    result = cursor.fetchone()
                    return dict(zip(columnNames, result))
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
