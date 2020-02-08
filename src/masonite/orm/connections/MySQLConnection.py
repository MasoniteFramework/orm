import pymysql


class MySQLConnection:
    _connection = None
    _cursor = None

    connections = {
        "host": "localhost",
        "username": "root",
        "password": "",
        "database": "orm",
        "port": "3306",
        "options": {"charset": "utf8mb4"},
    }

    def make_connection(self):

        """This sets the connection on the connection class
        """
        self._connection = pymysql.connect(
            cursorclass=pymysql.cursors.DictCursor, **self._get_connection_details()
        )

        return self

    def get_connection_details(self):
        """This is responsible for standardizing the normal connection
        details and passing it into the connection.
        """
        connection_details = {}
        connection_details.setdefault("db", self.connections.get("host"))
        connection_details.setdefault("user", self.connections.get("username"))
        connection_details.setdefault("password", self.connections.get("password"))
        connection_details.setdefault("port", self.connections.get("port"))
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

    def query(self, query, bindings):
        try:

            with self._connection.cursor() as cursor:
                # Read a single record
                cursor.execute(query, bindings)
                result = cursor.fetchone()
                return result
        finally:
            connection.close()
