from .mysql_grammar import MySQLGrammar
from .mssql_grammar import MSSQLGrammar
from .sqlite_grammar import SQLiteGrammar


class GrammarFactory:
    """Class for controlling the registration and creation of grammars.
    """

    grammars = {
        # Base grammars that will be used with various drivers
        "mysql": MySQLGrammar,
        "sqlite": SQLiteGrammar,
        "mssql": MSSQLGrammar,
        # examples of using different versions of grammar here
        "mssql2008": MSSQLGrammar,
        "mssql2012": MSSQLGrammar,
        "mssql2016": MSSQLGrammar,
    }

    @staticmethod
    def make(key):
        """Makes a specific registered grammar class from a key.

        Arguments:
            key {string} -- The key that the grammar is registered to.

        Returns:
            self
        """
        return GrammarFactory.grammars.get(key)
