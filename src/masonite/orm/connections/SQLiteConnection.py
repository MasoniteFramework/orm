import sqlite3


class SQLiteConnection:

    _connection = None
    _cursor = None

    connections = {
        "host": "localhost",
        "username": "root",
        "password": "",
        "database": "orm.db",
        "port": "3306",
        "options": {},
    }

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
        print(self.connections)
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

    @classmethod
    def set_connection_settings(cls, dictionary):
        """Transaction
        """
        cls.connection_details = dictionary

    def query(self, query, bindings, results="*"):

        query = query.replace("'?'", "?")
        print("make query", query, bindings)
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
