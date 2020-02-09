import pymysql


class MySQLConnection:
    _connection = None
    _cursor = None

    connection_details = {
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
        print("connecting with", self.get_connection_details())
        self._connection = pymysql.connect(
            cursorclass=pymysql.cursors.DictCursor, **self.get_connection_details()
        )

        print("alive?", self._connection.open)

        return self

    def get_connection_details(self):
        """This is responsible for standardizing the normal connection
        details and passing it into the connection.

        This will eventually be unpacked so make sure the keys are the same as the keywords
        that should pass to your connection method
        """
        connection_details = {}
        print("details are", self.connection_details)
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

    @classmethod
    def set_connection_settings(cls, dictionary):
        """Transaction
        """
        cls.connection_details = dictionary

    def query(self, query, bindings, results="*"):
        print("run query", query)
        query = query.replace("?", "%s")
        try:
            with self._connection.cursor() as cursor:
                # Read a single record
                cursor.execute(query, bindings)
                if results == 1:
                    result = cursor.fetchone()
                else:
                    result = cursor.fetchall()
                return result
        finally:
            self._connection.close()
