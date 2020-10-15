""" Database Settings """

import os

from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.connections import ConnectionResolver
from dotenv import load_dotenv
import logging

"""
|--------------------------------------------------------------------------
| Load Environment Variables
|--------------------------------------------------------------------------
|
| Loads in the environment variables when this page is imported.
|
"""

load_dotenv('.env')


"""
The connections here don't determine the database but determine the "connection".
They can be named whatever you want.
"""

DATABASES = {
    'default': 'mysql',
    'mysql': {
        'driver': 'mysql',
        'host': os.getenv('MYSQL_DATABASE_HOST'),
        'user': os.getenv('MYSQL_DATABASE_USER'),
        'password': os.getenv('MYSQL_DATABASE_PASSWORD'),
        'database': os.getenv('MYSQL_DATABASE_DATABASE'),
        'port': os.getenv('MYSQL_DATABASE_PORT'),
        'prefix': '',
        'options': {
            'charset': 'utf8mb4',
        },
    },
    'postgres': {
        'driver': 'postgres',
        'host': os.getenv('POSTGRES_DATABASE_HOST'),
        'user': os.getenv('POSTGRES_DATABASE_USER'),
        'password': os.getenv('POSTGRES_DATABASE_PASSWORD'),
        'database': os.getenv('POSTGRES_DATABASE_DATABASE'),
        'port': os.getenv('POSTGRES_DATABASE_PORT'),
        'prefix': '',
    },
    'sqlite': {
        'driver': 'sqlite',
        'database': 'orm.sqlite3',
        'prefix': ''
    }
}

ConnectionResolver.set_connection_details(DATABASES)

logger = logging.getLogger('masoniteorm.connection.queries')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    'It executed the query %(query)s'
)

handler = logging.StreamHandler()
# handler.setFormatter(formatter)

logger.addHandler(handler)

handler = logging.FileHandler("queries.log")
logger.addHandler(handler)


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
