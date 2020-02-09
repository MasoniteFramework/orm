from .mysql_grammar import MySQLGrammar
from .mssql_grammar import MSSQLGrammar


class GrammarFactory:

    grammars = {
        "mysql": MySQLGrammar,
        "mssql": MSSQLGrammar,
    }

    @staticmethod
    def make(key):
        grammar = GrammarFactory.grammars.get(key)
        if grammar:
            return grammar
