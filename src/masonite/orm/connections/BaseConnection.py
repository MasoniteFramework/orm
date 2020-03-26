from src.masonite.orm.grammar import GrammarFactory


class BaseConnection:

    _connection = None
    _cursor = None

    @classmethod
    def get_grammer(cls):
        """Gets a grammer using the connection details.

        If you specify a grammer in the connection detail you can
        override the grammar that gets returned. If you don't explicitly
        specify a grammer it will use the same grammer as the name of the driver.

        Returns:
            masonite.orm.grammar.Grammar -- A Masonite ORM Grammar class
        """
        if "grammer" in cls.connection_details:
            grammer_driver = cls.connection_details.get("grammer")
        else:
            grammer_driver = cls.connection_details.get("driver")

        return GrammarFactory().make(grammer_driver)

    @classmethod
    def set_connection_settings(cls, dictionary):
        """Class method to set the connection details to the class

        Arguments:
            dictionary {dict} -- A dictionary of connection information
        """
        cls.connection_details = dictionary
        if "options" not in cls.connection_details:
            cls.connection_details.setdefault("options", {})
