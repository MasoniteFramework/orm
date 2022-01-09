import os
import pytest
import unittest

from src.masoniteorm.config import db_url, load_config
from src.masoniteorm.exceptions import InvalidUrlConfiguration
from src.masoniteorm.connections import ConnectionResolver


class TestDbUrlHelper(unittest.TestCase):
    def setUp(self):
        self.original_db_url = os.getenv("DATABASE_URL")

    # def tearDown(self):
    #     os.environ["DATABASE_URL"] = self.original_db_url

    def test_parse_env_by_default(self):
        os.environ["DATABASE_URL"] = "mysql://root:@localhost:3306/orm"
        config = db_url()
        assert config.get("driver") == "mysql"

    # def test_raise_error_if_no_url(self):
    #     # no DATABASE_URL is defined yet
    #     with pytest.raises(InvalidUrlConfiguration):
    #         db_url()

    def test_parse_sqlite(self):
        # check in memory use
        config = db_url("sqlite://")
        assert config.get("driver", "sqlite")
        assert config.get("database", ":memory:")
        assert not config.get("user")
        config = db_url("sqlite://:memory:")
        assert config.get("driver", "sqlite")
        assert config.get("database", ":memory:")
        assert not config.get("user")
        config = db_url("sqlite://db.sqlite3")
        assert config.get("driver", "sqlite")
        assert config.get("database", "db.sqlite3")
        assert not config.get("user")

    def test_parse_mysql(self):
        config = db_url("mysql://root:@localhost:3306/orm")
        assert config == {
            "driver": "mysql",
            "database": "orm",
            "prefix": "",
            "options": {},
            "log_queries": False,
            "user": "root",
            "password": "",
            "host": "localhost",
            "port": 3306,
        }

    def test_parse_postgres(self):
        config = db_url(
            "postgres://utpcrbiihfqqys:de0a0d847094a66e32274262aa5b5f0ad78e5e34197875fc6089a2d9185d0032@ec2-54-225-242-183.compute-1.amazonaws.com:5432/da455n1ef8kout"
        )
        assert config == {
            "driver": "postgres",
            "database": "da455n1ef8kout",
            "prefix": "",
            "options": {},
            "log_queries": False,
            "user": "utpcrbiihfqqys",
            "password": "de0a0d847094a66e32274262aa5b5f0ad78e5e34197875fc6089a2d9185d0032",
            "host": "ec2-54-225-242-183.compute-1.amazonaws.com",
            "port": 5432,
        }

    def test_parse_mssql(self):
        config = db_url("mssql://john:secret@127.0.0.1:1433/mssql_db")
        assert config == {
            "driver": "mssql",
            "database": "mssql_db",
            "prefix": "",
            "options": {},
            "log_queries": False,
            "user": "john",
            "password": "secret",
            "host": "127.0.0.1",
            "port": "1433",
        }

    def test_parse_with_params(self):
        config = db_url(
            "mysql://root:@localhost:3306/orm",
            log_queries=True,
            prefix="a",
            options={"key": "value"},
        )
        assert config == {
            "driver": "mysql",
            "database": "orm",
            "prefix": "a",
            "options": {"key": "value"},
            "log_queries": True,
            "user": "root",
            "password": "",
            "host": "localhost",
            "port": 3306,
        }

    def test_using_it_with_connection_resolver(self):
        TEST_DATABASES = {
            "default": "test",
            "test": {
                **db_url("mysql://root:@localhost:3306/orm"),
                "prefix": "",
                "log_queries": True,
            },
        }
        resolver = ConnectionResolver().set_connection_details(TEST_DATABASES)
        config = resolver.get_connection_details().get("test")
        assert config.get("database") == "orm"
        assert config.get("user") == "root"
        assert config.get("password") == ""
        assert config.get("port") == 3306
        assert config.get("host") == "localhost"
        assert config.get("log_queries")
        # reset connection resolver to default for other tests to continue working
        from tests.integrations.config.database import DATABASES

        ConnectionResolver().set_connection_details(DATABASES)
