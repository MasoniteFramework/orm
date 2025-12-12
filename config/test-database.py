from src.masoniteorm.connections import ConnectionResolver

DATABASES = {
  "default": "mysql",
  "mysql": {
    "host": "127.0.0.1",
    "driver": "mysql",
    "database": "local",
    "user": "local",
    "password": "secret",
    "port": 3306,
    "log_queries": False,
    "options": {
      #
    }
  },
  "postgres": {
    "host": "127.0.0.1",
    "driver": "postgres",
    "database": "local",
    "user": "local",
    "password": "secret",
    "port": 5432,
    "log_queries": False,
    "options": {
      #
    }
  },
  "sqlite": {
    "driver": "sqlite",
    "database": "masonite.sqlite3",
  }
}

DB = ConnectionResolver().set_connection_details(DATABASES)
