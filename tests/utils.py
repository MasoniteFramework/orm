from unittest import mock

from src.masonite.orm.connections.ConnectionFactory import ConnectionFactory
from src.masonite.orm.connections.MySQLConnection import MySQLConnection
from src.masonite.orm.connections.SQLiteConnection import SQLiteConnection


class MockMySQLConnection(MySQLConnection):
    def make_connection(self):
        self._connection = mock.MagicMock()

        return self


class MockPostgresConnection(MySQLConnection):
    def make_connection(self):
        self._connection = mock.MagicMock()

        return self


class MockSQLiteConnection(SQLiteConnection):
    def make_connection(self):
        self._connection = mock.MagicMock()

        return self


class MockConnectionFactory(ConnectionFactory):
    _connections = {
        "mysql": MockMySQLConnection,
        "mssql": "",
        "postgres": MockPostgresConnection,
        "sqlite": MockSQLiteConnection,
        "oracle": "",
    }
