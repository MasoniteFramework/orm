import logging
from timeit import default_timer as timer


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
        self.log(query, bindings, query_time=end)
