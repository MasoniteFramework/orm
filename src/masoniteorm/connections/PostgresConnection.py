from ..exceptions import DriverNotFound, QueryException
from ..query.grammars import PostgresGrammar
from ..query.processors import PostgresPostProcessor
from ..schema.platforms import PostgresPlatform
from .BaseConnection import BaseConnection

CONNECTION_POOL = []

# All keyword arguments accepted directly by psycopg2.connect(), excluding
# 'options' which we build ourselves from leftover entries in self.options.
_PSYCOPG2_CONNECT_KWARGS = frozenset(
    {
        # Core identity
        "database",
        "dbname",
        "user",
        "password",
        "host",
        "port",
        # SSL
        "sslmode",
        "sslcert",
        "sslkey",
        "sslrootcert",
        "sslcrl",
        "sslpassword",
        # Timeouts & keepalives
        "connect_timeout",
        "keepalives",
        "keepalives_idle",
        "keepalives_interval",
        "keepalives_count",
        # Application identification
        "application_name",
        "fallback_application_name",
        # Misc
        "cursor_factory",
        "async",
    }
)


class PostgresConnection(BaseConnection):
    """Postgres Connection class."""

    name = "postgres"

    def __init__(
        self,
        host=None,
        database=None,
        user=None,
        port=None,
        password=None,
        prefix=None,
        options=None,
        full_details=None,
        name=None,
    ):
        self.host = host
        self.port = int(port) if port else None
        self.database = database
        self.user = user
        self.password = password

        self.prefix = prefix
        self.full_details = full_details or {}
        self.connection_pool_size = full_details.get(
            "connection_pooling_max_size", 100
        )
        self.options = options or {}
        self._cursor = None
        self.transaction_level = 0
        self.open = 0
        self.schema = None
        if name:
            self.name = name

    def _build_connect_kwargs(self):
        """Return a dict of kwargs ready to be unpacked into psycopg2.connect().

        self.options is partitioned into two groups:
        - Keys that are valid psycopg2.connect() keyword arguments are passed
          through directly.
        - All remaining keys are treated as PostgreSQL GUC parameters and
          appended to the ``options`` string as ``-c key=value`` entries
          alongside the schema search_path (when set).
        """
        # --- Base connection parameters ---------------------------------
        kwargs = {
            "database": self.database,
            "user": self.user,
            "password": self.password,
            "host": self.host,
            "port": self.port,
        }

        # --- Split self.options into direct kwargs vs GUC params --------
        guc_params = {}
        for key, value in self.options.items():
            if key in _PSYCOPG2_CONNECT_KWARGS:
                kwargs[key] = value
            else:
                guc_params[key] = value

        # --- Build the options / GUC string -----------------------------
        # search_path comes from the instance schema or full_details, but can
        # also be overridden via self.options by passing it as a leftover key.
        schema = self.schema or self.full_details.get("schema")
        if schema and "search_path" not in guc_params:
            guc_params["search_path"] = schema

        if guc_params:
            kwargs["options"] = " ".join(
                f"-c {k}={v}" for k, v in guc_params.items()
            )

        return kwargs

    def make_connection(self):
        """This sets the connection on the connection class"""
        if self.has_global_connection():
            return self.get_global_connection()

        self._connection = self.create_connection()

        self._connection.autocommit = True

        self.enable_disable_foreign_keys()

        self.open = 1

        return self

    def create_connection(self):
        try:
            import psycopg2
        except ModuleNotFoundError:
            raise DriverNotFound(
                "You must have the 'psycopg2' package installed to make a "
                "connection to Postgres. Please install it using "
                "'pip install psycopg2-binary'"
            )

        connect_kwargs = self._build_connect_kwargs()

        # Initialize the connection pool if the option is set
        initialize_size = self.full_details.get("connection_pooling_min_size")
        if (
            self.full_details.get("connection_pooling_enabled")
            and initialize_size
            and len(CONNECTION_POOL) < initialize_size
        ):
            for _ in range(initialize_size - len(CONNECTION_POOL)):
                CONNECTION_POOL.append(psycopg2.connect(**connect_kwargs))

        if (
            self.full_details.get("connection_pooling_enabled")
            and len(CONNECTION_POOL) > 0
        ):
            connection = CONNECTION_POOL.pop()
        else:
            connection = psycopg2.connect(**connect_kwargs)

        return connection

    def get_database_name(self):
        return self.database

    @classmethod
    def get_default_query_grammar(cls):
        return PostgresGrammar

    @classmethod
    def get_default_platform(cls):
        return PostgresPlatform

    @classmethod
    def get_default_post_processor(cls):
        return PostgresPostProcessor

    def reconnect(self):
        pass

    def close_connection(self):
        if (
            self.full_details.get("connection_pooling_enabled")
            and len(CONNECTION_POOL) < self.connection_pool_size
        ):
            CONNECTION_POOL.append(self._connection)
        else:
            self._connection.close()

        self._connection = None

    def commit(self):
        """Transaction"""
        if self.get_transaction_level() == 1:
            self._connection.commit()
            self._connection.autocommit = True

        self.transaction_level -= 1

    def begin(self):
        """Postgres Transaction"""
        self._connection.autocommit = False
        self.transaction_level += 1
        return self

    def rollback(self):
        """Transaction"""
        if self.get_transaction_level() == 1:
            self._connection.rollback()
            self._connection.autocommit = True

        self.transaction_level -= 1

    def get_transaction_level(self):
        """Transaction"""
        return self.transaction_level

    def set_cursor(self):
        from psycopg2.extras import RealDictCursor

        self._cursor = self._connection.cursor(cursor_factory=RealDictCursor)
        return self._cursor

    def query(self, query, bindings=(), results="*"):
        """Make the actual query that will reach the database and come back with a result.

        Arguments:
            query {string} -- A string query. This could be a qmarked string or a regular query.
            bindings {tuple} -- A tuple of bindings

        Keyword Arguments:
            results {str|1} -- If the results is equal to an asterisks it will call 'fetchAll'
                    else it will return 'fetchOne' and return a single record. (default: {"*"})

        Returns:
            dict|None -- Returns a dictionary of results or None
        """
        try:
            if not self._connection or self._connection.closed:
                self.make_connection()

            self.set_cursor()

            with self._cursor as cursor:
                if isinstance(query, list) and not self._dry:
                    for q in query:
                        self.statement(q, ())
                    return

                query = query.replace("?", "%s")
                self.statement(query, bindings)
                if results == 1:
                    return dict(cursor.fetchone() or {})
                else:
                    if "SELECT" in cursor.statusmessage:
                        return cursor.fetchall()
                    return {}
        except Exception as e:
            raise QueryException(str(e)) from e
        finally:
            if self.get_transaction_level() <= 0:
                self.open = 0
                self.close_connection()
