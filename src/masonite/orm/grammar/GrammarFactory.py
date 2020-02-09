from .mysql_grammar import MySQLGrammar
from .mssql_grammar import MSSQLGrammar
from .sqlite_grammar import SQLiteGrammar


class GrammarFactory:

    grammars = {
        # Base grammars that will be used with various drivers
        "mysql": MySQLGrammar,
        "sqlite": SQLiteGrammar,
        "mssql": MSSQLGrammar,
        # examples of using different versions of grammer here
        "mssql2008": MSSQLGrammar,
        "mssql2012": MSSQLGrammar,
        "mssql2016": MSSQLGrammar,
    }

    @staticmethod
    def make(key):
        grammar = GrammarFactory.grammars.get(key)
        if grammar:
            return grammar
