import pymysql

from .BaseConnection import BaseConnection


class MySQLConnection(BaseConnection):
    """MYSQL Connection class.
    """

    def make_connection(self):
        """This sets the connection on the connection class
        """
        self._connection = pymysql.connect(
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
            **self.get_connection_details(),
        )

        return self

    def get_connection_details(self):
        """This is responsible for standardizing the normal connection
        details and passing it into the connection.

        This will eventually be unpacked so make sure the keys are the same as the keywords
        that should pass to your connection method
        """
        connection_details = {}
        connection_details.setdefault("host", self.connection_details.get("host"))
        connection_details.setdefault("user", self.connection_details.get("username"))
        connection_details.setdefault(
            "password", self.connection_details.get("password")
        )
        connection_details.setdefault("port", int(self.connection_details.get("port")))
        connection_details.setdefault("db", self.connection_details.get("database"))
        connection_details.update(self.connection_details.get("options", {}))

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

    def transaction_level(self):
        """Transaction
        """
        pass

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
        print("running query", query)
        try:
            with self._connection.cursor() as cursor:
                cursor.execute(query, bindings)
                if results == 1:
                    return cursor.fetchone()
                else:
                    return cursor.fetchall()
        finally:
            self._connection.close()
