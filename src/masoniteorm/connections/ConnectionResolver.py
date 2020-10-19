class ConnectionResolver:

    _connection_details = {}

    def __init__(self):
        from ..connections import (
            SQLiteConnection,
            PostgresConnection,
            MySQLConnection,
            MSSQLConnection,
        )

        self.register(SQLiteConnection)
        self.register(PostgresConnection)
        self.register(MySQLConnection)
        self.register(MSSQLConnection)

    def set_connection_details(self, connection_details):
        self.__class__._connection_details = connection_details
        return self

    def get_connection_details(self):
        return self._connection_details

    def register(self, connection):
        from ..connections import ConnectionFactory

        ConnectionFactory.register(connection.name, connection)
