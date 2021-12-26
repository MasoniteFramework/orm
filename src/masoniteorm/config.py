import os
import pydoc
import urllib.parse as urlparse

from .exceptions import ConfigurationNotFound, InvalidUrlConfiguration


def load_config(config_path=None):
    """Load ORM configuration from given configuration path (dotted or not).
    If no path is provided:
        1. try to load from DB_CONFIG_PATH environment variable
        2. else try to load from default config_path: config/database
    """
    selected_config_path = (
        config_path or os.getenv("DB_CONFIG_PATH", None) or "config/database"
    )
    # format path as python module if needed
    selected_config_path = (
        selected_config_path.replace("/", ".").replace("\\", ".").rstrip(".py")
    )
    config_module = pydoc.locate(selected_config_path)
    if config_module is None:
        raise ConfigurationNotFound(
            f"ORM configuration file has not been found in {selected_config_path}."
        )
    return config_module


def db_url(database_url=None, prefix="", options={}, log_queries=False):
    """Parse connection configuration from database url format. If no url is provided,
    DATABASE_URL environment variable will be used instead.

    Reference: Code adapted from https://github.com/jacobian/dj-database-url
    """

    url = database_url or os.getenv("DATABASE_URL")
    if not url:
        raise InvalidUrlConfiguration("Database url is empty !")

    # Register database schemes in URLs.
    urlparse.uses_netloc.append("postgres")
    urlparse.uses_netloc.append("postgresql")
    urlparse.uses_netloc.append("pgsql")
    urlparse.uses_netloc.append("postgis")
    urlparse.uses_netloc.append("mysql")
    urlparse.uses_netloc.append("mysql2")
    urlparse.uses_netloc.append("mysqlgis")
    urlparse.uses_netloc.append("mssql")
    urlparse.uses_netloc.append("sqlite")

    DRIVERS_MAP = {
        "postgres": "postgres",
        "postgresql": "postgres",
        "pgsql": "postgres",
        "postgis": "postgres",
        "mysql": "mysql",
        "mysql2": "mysql",
        "mysqlgis": "mysql",
        "mysql-connector": "mysql",
        "mssql": "mssql",
        "sqlite": "sqlite",
    }

    # this is a special case, because if we pass this URL into
    # urlparse, urlparse will choke trying to interpret "memory"
    # as a port number
    if url in ["sqlite://:memory:", "sqlite://memory"]:
        driver = DRIVERS_MAP["sqlite"]
        path = ":memory:"
    # otherwise parse the url as normal
    else:
        url = urlparse.urlparse(url)
        # remove query string from path (not parsed for now)
        path = url.path[1:]
        if "?" in path and not url.query:
            path, _ = path.split("?", 2)

        # if we are using sqlite and we have no path, then assume we
        # want an in-memory database (this is the behaviour of sqlalchemy)
        if url.scheme == "sqlite" and path == "":
            path = ":memory:"

        # handle postgres percent-encoded paths.
        hostname = url.hostname or ""
        if "%2f" in hostname.lower():
            # Switch to url.netloc to avoid lower cased paths
            hostname = url.netloc
            if "@" in hostname:
                hostname = hostname.rsplit("@", 1)[1]
            if ":" in hostname:
                hostname = hostname.split(":", 1)[0]
            hostname = hostname.replace("%2f", "/").replace("%2F", "/")

        # lookup specified driver
        driver = DRIVERS_MAP[url.scheme]
        port = (
            str(url.port) if url.port and driver in [DRIVERS_MAP["mssql"]] else url.port
        )

    # build final configuration
    config = {
        "driver": driver,
        "database": urlparse.unquote(path or ""),
        "prefix": prefix,
        "options": options,
        "log_queries": log_queries,
    }

    if driver != DRIVERS_MAP["sqlite"]:
        config.update(
            {
                "user": urlparse.unquote(url.username or ""),
                "password": urlparse.unquote(url.password or ""),
                "host": hostname,
                "port": port or "",
            }
        )
    return config
