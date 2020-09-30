import random

from ..exceptions import DriverNotFound
from .BaseConnection import BaseConnection

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
        options={},
    ):
        self.host = host
        self.port = port
        if str(port).isdigit():
            self.port = int(self.port)
        self.database = database
        self.user = user
        self.password = password
        self.prefix = prefix
        self.options = options
        self._cursor = None
        self.transaction_level = 0

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

        return self

    def reconnect(self):
        self._connection.connect()
        return self

    def get_connection_details(self):
        """This is responsible for standardizing the normal connection
        details and passing it into the connection.

        This will eventually be unpacked so make sure the keys are the same as the keywords
        that should pass to your connection method
        """
        connection_details = {}
        connection_details.setdefault("host", self.connection_details.get("host"))
        connection_details.setdefault("user", self.connection_details.get("user"))
        connection_details.setdefault(
            "password", self.connection_details.get("password")
        )
        connection_details.setdefault("port", int(self.connection_details.get("port")))
        connection_details.setdefault("db", self.connection_details.get("database"))
        connection_details.update(self.connection_details.get("options", {}))

        return connection_details

    @classmethod
    def get_database_name(self):
        return self().get_connection_details().get("db")

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
        query = query.replace("'?'", "%s")
        print("running query", query, bindings)

        if self._dry:
            return {}

        if not self._connection.open:
            self._connection.connect()

        try:
            with self._connection.cursor() as cursor:
                cursor.execute(query, bindings)
                if results == 1:
                    return cursor.fetchone()
                else:
                    return cursor.fetchall()
        except Exception as e:
            raise e
        finally:
            if self.get_transaction_level() <= 0:
                self._connection.close()
