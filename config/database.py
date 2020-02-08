""" Database Settings """

import os

from masonite.environment import LoadEnvironment, env
from orator import DatabaseManager, Model


"""
|--------------------------------------------------------------------------
| Load Environment Variables
|--------------------------------------------------------------------------
|
| Loads in the environment variables when this page is imported.
|
"""

LoadEnvironment()

"""
|--------------------------------------------------------------------------
| Database Settings
|--------------------------------------------------------------------------
|
| Set connection database settings here as a dictionary. Follow the
| format below to create additional connection settings.
|
| @see Orator migrations documentation for more info
|
"""

DATABASES = {
    'default': os.environ.get('DB_DRIVER'),
    'sqlite': {
        'driver': 'sqlite',
        'database': os.environ.get('DB_DATABASE')
    },
    'postgres': {
        'driver': 'postgres',
        'host': env('DB_HOST'),
        'database': env('DB_DATABASE'),
        'port': env('DB_PORT'),
        'user': env('DB_USERNAME'),
        'password': env('DB_PASSWORD'),
        'log_queries': env('DB_LOG'),
    },
}

DB = DatabaseManager(DATABASES)
Model.set_connection_resolver(DB)
