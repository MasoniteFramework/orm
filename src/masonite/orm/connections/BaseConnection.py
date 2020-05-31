from ..grammar import GrammarFactory


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
            masonite.orm.grammar.Grammar -- A Masonite ORM Grammar class
        """
        if "grammar" in cls.connection_details:
            grammar_driver = cls.connection_details.get("grammar")
        else:
            grammar_driver = cls.connection_details.get("driver")

        return GrammarFactory().make(grammar_driver)

    @classmethod
    def set_connection_settings(cls, dictionary):
        """Class method to set the connection details to the class

        Arguments:
            dictionary {dict} -- A dictionary of connection information
        """
        cls.connection_details = dictionary
        if "options" not in cls.connection_details:
            cls.connection_details.setdefault("options", {})

    @classmethod
    def dry(cls):
        cls._dry = True
        return cls
