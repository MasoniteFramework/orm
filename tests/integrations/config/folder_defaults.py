from src.masoniteorm.connections import ConnectionResolver


DATABASES = {
    "default": "test",
    "test": {
        "driver": "sqlite",
        "database": "orm.sqlite3",
        "prefix": "",
        "log_queries": True,
    },
}

DB = ConnectionResolver().set_connection_details(DATABASES)

MODELS_DIRECTORY = "custom-app"
MIGRATIONS_DIRECTORY = "custom-databases/migrations"
SEEDS_DIRECTORY = "custom-databases/seeds"
SEEDERS_DIRECTORY = "custom-databases/seeds"