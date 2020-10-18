class ConnectionResolver:

    _connection_details = {}

    def __init__(self):
        from ..connectors import SQLiteConnector, PostgresConnector, MySQLConnector
        self.register(SQLiteConnector())
        self.register(PostgresConnector())
        self.register(MySQLConnector())

    def set_connection_details(self, connection_details):
        self.__class__._connection_details = connection_details
        return self

    def get_connection_details(self):
        return self._connection_details

    def register(self, connector):
        from ..connections import ConnectionFactory
        ConnectionFactory.register(connector.name, connector.get_connection())
