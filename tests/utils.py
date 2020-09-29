from unittest import mock

from src.masoniteorm.connections.ConnectionFactory import ConnectionFactory
from src.masoniteorm.connections.MySQLConnection import MySQLConnection
from src.masoniteorm.connections.SQLiteConnection import SQLiteConnection


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

    def query(self, *args, **kwargs):
        return {}


class MockConnectionFactory(ConnectionFactory):
    _connections = {
        "mysql": MockMySQLConnection,
        "mssql": "",
        "postgres": MockPostgresConnection,
        "sqlite": MockSQLiteConnection,
        "oracle": "",
    }
