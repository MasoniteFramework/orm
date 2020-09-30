""" Database Settings """

import os

from src.masoniteorm.query import QueryBuilder
from src.masoniteorm.connections import ConnectionResolver

"""
|--------------------------------------------------------------------------
| Load Environment Variables
|--------------------------------------------------------------------------
|
| Loads in the environment variables when this page is imported.
|
"""


"""
The connections here don't determine the database but determine the "connection".
They can be named whatever you want.
"""

DATABASES = {
    'default': 'mysql',
    'mysql': {
        'driver': 'mysql',
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'orm',
        'port': '3306',
        'prefix': '',
        'grammar': 'mysql',
        'options': {
            'charset': 'utf8mb4',
        },
    },
    'postgres': {
        'driver': 'postgres',
        'host': 'localhost',
        'user': 'postgres',
        'password': 'postgres',
        'database': 'personal',
        'port': '5432',
        'prefix': '',
        'grammar': 'postgres',
    },
    'sqlite': {
        'driver': 'sqlite',
        'database': 'orm.sqlite3',
        'prefix': ''
    }
}

ConnectionResolver.set_connection_details(DATABASES)

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
