import random

from ..exceptions import DriverNotFound
from .BaseConnection import BaseConnection
from ..query.grammars import MySQLGrammar
from ..schema.platforms import MySQLPlatform
from ..query.processors import MySQLPostProcessor
from ..exceptions import QueryException

CONNECTION_POOL = []


class MySQLConnection(BaseConnection):
    """MYSQL Connection class."""

    name = "mysql"
    _dry = False

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
        self.port = port
        if str(port).isdigit():
            self.port = int(self.port)
        self.database = database
        self.user = user
        self.password = password
        self.prefix = prefix
        self.full_details = full_details or {}
        self.options = options or {}
        self._cursor = None
        self.open = 0
        self.transaction_level = 0
        if name:
            self.name = name

    def make_connection(self):
        """This sets the connection on the connection class"""

        if self._dry:
            return

        try:
            import pymysql
        except ModuleNotFoundError:
            raise DriverNotFound(
                "You must have the 'pymysql' package installed to make a connection to MySQL. Please install it using 'pip install pymysql'"
            )

        if self.has_global_connection():
            return self.get_global_connection()

        self._connection = pymysql.connect(
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port,
            db=self.database,
            **self.options
        )
        self.open = 1

        return self

    def reconnect(self):
        self._connection.connect()
        return self

    @classmethod
    def get_default_query_grammar(cls):
        return MySQLGrammar

    @classmethod
    def get_default_platform(cls):
        return MySQLPlatform

    @classmethod
    def get_default_post_processor(cls):
        return MySQLPostProcessor

    def get_database_name(self):
        return self.database

    def commit(self):
        """Transaction"""
        self._connection.commit()
        self.transaction_level -= 1

    def dry(self):
        """Transaction"""
        self._dry = True
        return self

    def begin(self):
        """Mysql Transaction"""
        self._connection.begin()
        self.transaction_level += 1
        return self

    def rollback(self):
        """Transaction"""
        self._connection.rollback()
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

        if self._dry:
            return {}

        if not self._connection.open:
            self._connection.connect()

        self._cursor = self._connection.cursor()

        try:
            with self._cursor as cursor:
                if isinstance(query, list):
                    for q in query:
                        q = q.replace("'?'", "%s")
                        self.statement(q, ())
                    return

                query = query.replace("'?'", "%s")
                self.statement(query, bindings)
                if results == 1:
                    return self.format_cursor_results(cursor.fetchone())
                else:
                    return self.format_cursor_results(cursor.fetchall())
        except Exception as e:
            raise QueryException(str(e)) from e
        finally:
            if self.get_transaction_level() <= 0:
                self.open = 0
                self._connection.close()
