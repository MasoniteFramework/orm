import sqlite3
from ..grammar import GrammarFactory
from .BaseConnection import BaseConnection


class SQLiteConnection(BaseConnection):
    """SQLite Connection class.
    """

    name = "sqlite"
    _connection = None

    def make_connection(self):
        """This sets the connection on the connection class
        """
        connection_details = self.get_connection_details()
        if self.__class__._connection:
            return self
        self.__class__._connection = sqlite3.connect(
            connection_details.get("db"), isolation_level=None
        )
        self.__class__._connection.row_factory = sqlite3.Row

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
        connection_details.setdefault(
            "db", self.connection_details.get("database"))
        connection_details.update(self.connection_details.get("options", {}))

        return connection_details

    def reconnect(self):
        pass

    def commit(self):
        """Transaction
        """
        print('commit transaction')
        return self.__class__._connection.commit()

    def begin(self):
        """Transaction
        """
        print('starting sqlite transaction', self, self.__class__._connection)
        self.__class__._connection.isolation_level = 'DEFERRED'
        return self.__class__._connection

    def rollback(self):
        """Transaction
        """
        print('rolling back transaction', self, self.__class__._connection)
        self.__class__._connection.rollback()

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
        print("running query: ", query)
        try:
            cursor = self.__class__._connection.cursor()
            cursor.execute(query, bindings)
            if results == 1:
                result = [dict(row) for row in cursor.fetchall()]
                if result:
                    return result[0]
            else:
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            if self.__class__._connection and self.__class__._connection.isolation_level:
                self.rollback()
            raise e

