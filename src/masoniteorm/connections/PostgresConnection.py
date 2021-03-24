from ..exceptions import DriverNotFound
from .BaseConnection import BaseConnection
from ..query.grammars import PostgresGrammar
from ..schema.platforms import PostgresPlatform
from ..query.processors import PostgresPostProcessor
from ..exceptions import QueryException


CONNECTION_POOL = []


class PostgresConnection(BaseConnection):
    """Postgres Connection class."""

    name = "postgres"

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
            import psycopg2
        except ModuleNotFoundError:
            raise DriverNotFound(
                "You must have the 'psycopg2' package installed to make a connection to Postgres. Please install it using 'pip install psycopg2-binary'"
            )

        if self.has_global_connection():
            return self.get_global_connection()

        self._connection = psycopg2.connect(
            database=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )

        self._connection.autocommit = True

        self.open = 1

        return self

    def get_database_name(self):
        return self.database

    @classmethod
    def get_default_query_grammar(cls):
        return PostgresGrammar

    @classmethod
    def get_default_platform(cls):
        return PostgresPlatform

    @classmethod
    def get_default_post_processor(cls):
        return PostgresPostProcessor

    def reconnect(self):
        pass

    def commit(self):
        """Transaction"""
        if self.get_transaction_level() == 1:
            self._connection.commit()
            self._connection.autocommit = True

        self.transaction_level -= 1

    def begin(self):
        """Postgres Transaction"""
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

    def set_cursor(self):
        from psycopg2.extras import RealDictCursor

        self._cursor = self._connection.cursor(cursor_factory=RealDictCursor)
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
            if self._connection.closed:
                self.make_connection()

            self.set_cursor()

            with self._cursor as cursor:
                if isinstance(query, list) and not self._dry:
                    for q in query:
                        self.statement(q, ())
                    return

                query = query.replace("'?'", "%s")
                self.statement(query, bindings)
                if results == 1:
                    return dict(cursor.fetchone() or {})
                else:
                    if "SELECT" in cursor.statusmessage:
                        return cursor.fetchall()
                    return {}
        except Exception as e:
            raise QueryException(str(e)) from e
        finally:
            if self.get_transaction_level() <= 0:
                self.open = 0
                self._connection.close()
