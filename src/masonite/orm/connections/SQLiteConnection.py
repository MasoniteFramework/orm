import sqlite3
from ..grammar import GrammarFactory
from .BaseConnection import BaseConnection


class SQLiteConnection(BaseConnection):
    """SQLite Connection class.
    """

    def make_connection(self):
        """This sets the connection on the connection class
        """
        connection_details = self.get_connection_details()
        self._connection = sqlite3.connect(connection_details.get("db"))
        self._connection.row_factory = sqlite3.Row

        return self

    def get_connection_details(self):
        """This is responsible for standardizing the normal connection
        details and passing it into the connection.

        This will eventually be unpacked so make sure the keys are the same as the keywords
        that should pass to your connection method
        """
        connection_details = {}
        connection_details.setdefault("db", self.connections.get("database"))
        connection_details.update(self.connections.get("options", {}))

        return connection_details

    def reconnect(self):
        pass

    def commit(self):
        """Transaction
        """
        pass

    def begin_transaction(self):
        """Transaction
        """
        pass

    def rollback(self):
        """Transaction
        """
        pass

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
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, bindings)
            if results == 1:
                result = [dict(row) for row in cursor.fetchall()]
                if result:
                    return result[0]
            else:
                return [dict(row) for row in cursor.fetchall()]
        finally:
            self._connection.close()
