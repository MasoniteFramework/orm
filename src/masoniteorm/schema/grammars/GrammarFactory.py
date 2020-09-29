from .SQLiteGrammar import SQLiteGrammar
from .MySQLGrammar import MySQLGrammar
from .PostgresGrammar import PostgresGrammar


class GrammarFactory:
    """Class for controlling the registration and creation of grammars."""

    grammars = {
        # Base grammars that will be used with various drivers
        "sqlite": SQLiteGrammar,
        "mysql": MySQLGrammar,
        "postgres": PostgresGrammar
        # examples of using different versions of grammar here
    }

    @staticmethod
    def make(key):
        """Makes a specific registered grammar class from a key.

        Arguments:
            key {string} -- The key that the grammar is registered to.

        Returns:
            self
        """
        from config.database import DATABASES
        if key == "default":
            key = DATABASES.get(key)

        return GrammarFactory.grammars.get(key)
