from ..query.grammars import SQLiteGrammar
from .BaseConnection import BaseConnection
from ..schema.platforms import SQLitePlatform
from ..query.processors import SQLitePostProcessor
from ..exceptions import QueryException


class SQLiteConnection(BaseConnection):
    """SQLite Connection class."""

    name = "sqlite"

    _connection = None

    def __init__(
        self,
        host=None,
        database=None,
        user=None,
        port=None,
        password=None,
        prefix=None,
        full_details=None,
        options=None,
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
            import sqlite3
        except ModuleNotFoundError:
            raise DriverNotFound(
                "You must have the 'sqlite3' package installed to make a connection to MySQL. Please install it using 'pip install pymysql'"
            )

        if self.has_global_connection():
            return self.get_global_connection()

        self._connection = sqlite3.connect(self.database, isolation_level=None)

        self._connection.row_factory = sqlite3.Row
        self.open = 1

        return self

    @classmethod
    def get_default_query_grammar(cls):
        return SQLiteGrammar

    @classmethod
    def get_default_platform(cls):
        return SQLitePlatform

    @classmethod
    def get_default_post_processor(cls):
        return SQLitePostProcessor

    def get_database_name(self):
        return self.database

    def reconnect(self):
        pass

    def commit(self):
        """Transaction"""

        if self.get_transaction_level() == 1:
            self.transaction_level -= 1
            self._connection.commit()
            self._connection.isolation_level = None
            self._connection.close()
            self.open = 0

        self.transaction_level -= 1
        return self

    def begin(self):
        """Sqlite Transaction"""
        self._connection.isolation_level = "DEFERRED"
        self.transaction_level += 1
        return self

    def rollback(self):
        """Transaction"""
        if self.get_transaction_level() == 1:
            self.transaction_level -= 1
            self._connection.rollback()
            self._connection.close()
            self.open = 0

        self.transaction_level -= 1
        return self

    def get_cursor(self):
        return self._cursor

    def get_transaction_level(self):
        return self.transaction_level

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
        if not self.open:
            self.make_connection()

        try:
            self._cursor = self._connection.cursor()

            if isinstance(query, list):
                for query in query:
                    self.statement(query)
            else:
                query = query.replace("'?'", "?")
                self.statement(query, bindings)
                if results == 1:
                    result = [dict(row) for row in self._cursor.fetchall()]
                    if result:
                        return result[0]
                else:
                    return [dict(row) for row in self._cursor.fetchall()]
        except Exception as e:
            raise QueryException(str(e)) from e
        finally:
            if self.get_transaction_level() <= 0:
                self._connection.close()
                self.open = 0

    def format_cursor_results(self, cursor_result):
        return [dict(row) for row in cursor_result]

    def select_many(self, query, bindings, amount):
        self._cursor = self._connection.cursor()
        self.statement(query)
        if not self.open:
            self.make_connection()

        result = self.format_cursor_results(self._cursor.fetchmany(amount))
        while result:
            yield result

            result = self.format_cursor_results(self._cursor.fetchmany(amount))
