from unittest import mock

from src.masoniteorm.connections.ConnectionFactory import ConnectionFactory
from src.masoniteorm.connections.MySQLConnection import MySQLConnection
from src.masoniteorm.connections.SQLiteConnection import SQLiteConnection
from src.masoniteorm.schema.platforms import MySQLPlatform


class MockMySQLConnection(MySQLConnection):
    def make_connection(self):
        self._connection = mock.MagicMock()
        self._cursor = mock.MagicMock()

        return self

    @classmethod
    def get_default_platform(cls):
        return MySQLPlatform


class MockMSSQLConnection(MySQLConnection):
    def make_connection(self):
        self._connection = mock.MagicMock()
        self._cursor = mock.MagicMock()

        return self

    @classmethod
    def get_default_platform(cls):
        return MySQLPlatform


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
        "mssql": MockMSSQLConnection,
        "postgres": MockPostgresConnection,
        "sqlite": MockSQLiteConnection,
        "oracle": "",
    }
