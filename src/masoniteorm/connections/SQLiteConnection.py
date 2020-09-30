import sqlite3
from ..query.grammars import GrammarFactory
from .BaseConnection import BaseConnection


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
        options={},
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
        self.options = options
        self._cursor = None
        self.transaction_level = 0

    def make_connection(self):
        """This sets the connection on the connection class"""
        print("db", self.database)

        self._connection = sqlite3.connect(self.database, isolation_level=None)

        self._connection.row_factory = sqlite3.Row

        return self

    @classmethod
    def get_database_name(self):
        return self().get_connection_details().get("db")

    def get_connection_details(self):
        """This is responsible for standardizing the normal connection
        details and passing it into the connection.

        This will eventually be unpacked so make sure the keys are the same as the keywords
        that should pass to your connection method
        """
        connection_details = {}
        connection_details.setdefault("db", self.connection_details.get("database"))
        connection_details.update(self.connection_details.get("options", {}))

        return connection_details

    def reconnect(self):
        pass

    def commit(self):
        """Transaction"""
        if self.get_transaction_level() == 1:
            self._connection.commit()
            self._connection.isolation_level = None

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
            self._connection.rollback()
            self._connection.isolation_level = None

        self.transaction_level -= 1
        return self

    def get_cursor(self):
        return self._cursor

    def get_transaction_level(self):
        return self.transaction_level

    def query(self, query, bindings, results="*"):
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
        query = query.replace("'?'", "?")
        print("running query: ", self, query, bindings)
        try:
            self._cursor = self._connection.cursor()
            self._cursor.execute(query, bindings)
            if results == 1:
                result = [dict(row) for row in self._cursor.fetchall()]
                if result:
                    return result[0]
            else:
                return [dict(row) for row in self._cursor.fetchall()]
        except Exception as e:
            raise e
        finally:
            if self.get_transaction_level() <= 0:
                self._connection.close()
