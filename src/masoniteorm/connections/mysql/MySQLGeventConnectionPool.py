import gevent
from ..BaseConnection import BaseConnection
from ...query.grammars import MySQLGrammar
from ...schema.platforms import MySQLPlatform
from ...query.processors import MySQLPostProcessor
from ...exceptions import QueryException
from .MySQLSingleConnection import MySQLSingleConnection

DESIRED_POOL_NUMBER = 10
MAX_POOL_NUMBER = 100


class MySQLGeventConnectionPool(BaseConnection):
    """MYSQL Connection class."""

    name = "mysql_geventpool"
    _dry = False
    _pool = []

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
        self.transaction_level = 0
        if name:
            self.name = name

    def get_or_make(self) -> MySQLSingleConnection:
        gid = id(gevent.getcurrent())
        for pool in self.__class__._pool:
            pid, conn = pool
            if pid == gid:
                return conn

        self.clean_up()
        conn = self.new()
        self.__class__._pool.insert(0, (gid, conn))
        return conn

    def new(self):
        if self._dry:
            return
        connection = MySQLSingleConnection()
        connection.connect(
            autocommit=True,
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port,
            db=self.database,
            **self.options
        )
        return connection

    def clean_up(self):
        if len(self.__class__._pool) < DESIRED_POOL_NUMBER:
            return True
        if len(self.__class__._pool) >= MAX_POOL_NUMBER:
            (pid, conn) = self.__class__._pool.pop()
            conn.close()
        for _ in range(len(self.__class__._pool)):
            (pid, conn) = self.__class__._pool.pop()
            if conn.transaction_level > 0:
                self.__class__._pool.insert(0, (pid, conn))
            else:
                conn.close()
                return True
        return True

    def make_connection(self):
        self.get_or_make()
        return self

    def reconnect(self):
        self.get_or_make().reconnect()
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

    def dry(self):
        self._dry = True
        return self

    def commit(self):
        """Transaction"""
        connection = self.get_or_make()
        connection.commit()
        connection.transaction_level -= 1

    def begin(self):
        """Mysql Transaction"""
        connection = self.get_or_make()
        connection.begin()
        connection.transaction_level += 1
        return self

    def rollback(self):
        """Transaction"""
        connection = self.get_or_make()
        connection.rollback()
        connection.transaction_level -= 1

    def get_transaction_level(self):
        """Transaction"""
        connection = self.get_or_make()
        return connection.transaction_level

    def get_cursor(self):
        return self.get_or_make().get_cursor()

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

        connection = self.get_or_make()
        self._cursor = connection.cursor()

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
