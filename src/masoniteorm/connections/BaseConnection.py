import logging
from timeit import default_timer as timer
from .ConnectionResolver import ConnectionResolver


class BaseConnection:

    _connection = None
    _cursor = None
    _dry = False

    def dry(self):
        self._dry = True
        return self

    def log(
        self, query, bindings, query_time=0, logger="masoniteorm.connections.queries"
    ):
        logger = logging.getLogger("masoniteorm.connection.queries")
        logger.debug(
            f"Running query {query}, {bindings}. Executed in {query_time}ms",
            extra={"query": query, "bindings": bindings, "query_time": query_time},
        )

    def statement(self, query, bindings=()):
        """Wrapper around calling the cursor query. Helpful for logging output.

        Args:
            query (string): The query to execute on the cursor
            bindings (tuple, optional): Tuple of query bindings. Defaults to ().
        """
        start = timer()
        if not self._cursor:
            raise AttributeError(
                f"Must set the _cursor attribute on the {self.__class__.__name__} class before calling the 'statement' method."
            )

        self._cursor.execute(query, bindings)
        end = "{:.2f}".format(timer() - start)

        if self.full_details and self.full_details.get("log_queries", False):
            self.log(query, bindings, query_time=end)

    def has_global_connection(self):
        return self.name in ConnectionResolver().get_global_connections()

    def get_global_connection(self):
        return ConnectionResolver().get_global_connections()[self.name]

    def enable_query_log(self):
        self.full_details["log_queries"] = True

    def disable_query_log(self):
        self.full_details["log_queries"] = False

    def format_cursor_results(self, cursor_result):
        return cursor_result

    def set_cursor(self):
        self._cursor = self._connection.cursor()
        return self

    def select_many(self, query, bindings, amount):
        self.set_cursor()
        self.statement(query)
        if not self.open:
            self.make_connection()

        result = self.format_cursor_results(self._cursor.fetchmany(amount))
        while result:
            yield result

            result = self.format_cursor_results(self._cursor.fetchmany(amount))
