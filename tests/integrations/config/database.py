""" Database Settings """
import os
import logging

from dotenv import load_dotenv

from src.masoniteorm.connections import ConnectionResolver
from src.masoniteorm.config import db_url

"""
|--------------------------------------------------------------------------
| Load Environment Variables
|--------------------------------------------------------------------------
|
| Loads in the environment variables when this page is imported.
|
"""

load_dotenv(".env")


"""
The connections here don't determine the database but determine the "connection".
They can be named whatever you want.
"""

DATABASES = {
    "default": "mysql",
    "mysql": {
        "driver": "mysql",
        "host": os.getenv("MYSQL_DATABASE_HOST"),
        "user": os.getenv("MYSQL_DATABASE_USER"),
        "password": os.getenv("MYSQL_DATABASE_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE_DATABASE"),
        "port": os.getenv("MYSQL_DATABASE_PORT"),
        "prefix": "",
        "options": {"charset": "utf8mb4"},
        "log_queries": True,
        "propagate": False,
    },
    "t": {"driver": "sqlite", "database": "orm.sqlite3", "log_queries": True, "foreign_keys": True},
    "devprod": {
        "driver": "mysql",
        "host": os.getenv("MYSQL_DATABASE_HOST"),
        "user": os.getenv("MYSQL_DATABASE_USER"),
        "password": os.getenv("MYSQL_DATABASE_PASSWORD"),
        "database": "DEVPROD",
        "port": os.getenv("MYSQL_DATABASE_PORT"),
        "prefix": "",
        "options": {"charset": "utf8mb4"},
        "log_queries": True,
        "propagate": False,
    },
    "many": {
        "driver": "mysql",
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "replicate",
        "port": os.getenv("MYSQL_DATABASE_PORT"),
        "options": {"charset": "utf8mb4"},
        "log_queries": True,
        "propagate": False,
    },
    "postgres": {
        "driver": "postgres",
        "host": os.getenv("POSTGRES_DATABASE_HOST"),
        "user": os.getenv("POSTGRES_DATABASE_USER"),
        "password": os.getenv("POSTGRES_DATABASE_PASSWORD"),
        "database": os.getenv("POSTGRES_DATABASE_DATABASE"),
        "port": os.getenv("POSTGRES_DATABASE_PORT"),
        "prefix": "",
        "log_queries": True,
        "propagate": False,
    },
    # Example with db_url()
    # "postgres": db_url(
    #     "postgres://user:@localhost:5432/postgres", log_queries=True
    # ),
    "dev": {
        "driver": "sqlite",
        "database": "orm.sqlite3",
        "prefix": "",
        "log_queries": True,
    },
    # Example with db_url()
    # "dev": {**db_url("sqlite://orm.sqlite3"), "prefix": "", "log_queries": True},
    "mssql": {
        "driver": "mssql",
        "host": os.getenv("MSSQL_DATABASE_HOST"),
        "user": os.getenv("MSSQL_DATABASE_USER"),
        "password": os.getenv("MSSQL_DATABASE_PASSWORD"),
        "database": os.getenv("MSSQL_DATABASE_DATABASE"),
        "port": os.getenv("MSSQL_DATABASE_PORT"),
        "prefix": "",
        "log_queries": True,
        "options": {
            "trusted_connection": "Yes",
            "integrated_security": "sspi",
            "instance": "SQLExpress",
            "authentication": "ActiveDirectoryPassword",
            "driver": "ODBC Driver 17 for SQL Server",
            "connection_timeout": 15,
        },
    },
}

DB = ConnectionResolver().set_connection_details(DATABASES)

logger = logging.getLogger("masoniteorm.connection.queries")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("It executed the query %(query)s")

stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler("queries.log")

logger.addHandler(stream_handler)
logger.addHandler(file_handler)


# DB = QueryBuilder(connection_details=DATABASES)

# DATABASES = {
#     'default': os.environ.get('DB_DRIVER'),
#     'sqlite': {
#         'driver': 'sqlite',
#         'database': os.environ.get('DB_DATABASE')
#     },
#     'postgres': {
#         'driver': 'postgres',
#         'host': env('DB_HOST'),
#         'database': env('DB_DATABASE'),
#         'port': env('DB_PORT'),
#         'user': env('DB_USERNAME'),
#         'password': env('DB_PASSWORD'),
#         'log_queries': env('DB_LOG'),
#     },
# }

# DB = DatabaseManager(DATABASES)
# Model.set_connection_resolver(DB)
