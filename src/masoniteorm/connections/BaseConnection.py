from ..query.grammars import GrammarFactory
import logging
from timeit import default_timer as timer


class BaseConnection:

    _connection = None
    _cursor = None
    _dry = False

    @classmethod
    def get_grammar(cls):
        """Gets a grammar using the connection details.

        If you specify a grammar in the connection detail you can
        override the grammar that gets returned. If you don't explicitly
        specify a grammar it will use the same grammar as the name of the driver.

        Returns:
            masoniteorm.grammar.Grammar -- A Masonite ORM Grammar class
        """
        if "grammar" in cls.connection_details:
            grammar_driver = cls.connection_details.get("grammar")
        else:
            grammar_driver = cls.connection_details.get("driver")

        return GrammarFactory().make(grammar_driver)

    @classmethod
    def get_schema_grammar(cls):
        """Gets a grammar using the connection details.

        If you specify a grammar in the connection detail you can
        override the grammar that gets returned. If you don't explicitly
        specify a grammar it will use the same grammar as the name of the driver.

        Returns:
            masonite.orm.grammar.Grammar -- A Masonite ORM Grammar class
        """
        if "grammar" in cls.connection_details:
            grammar_driver = cls.connection_details.get("grammar")
        else:
            grammar_driver = cls.connection_details.get("driver")

        return SchemaGrammarFactory().make(grammar_driver)

    @classmethod
    def set_connection_settings(cls, dictionary):
        """Class method to set the connection details to the class

        Arguments:
            dictionary {dict} -- A dictionary of connection information
        """
        cls.connection_details = dictionary
        if "options" not in cls.connection_details:
            cls.connection_details.setdefault("options", {})

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
