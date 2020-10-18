from ..connections import SQLiteConnection
from ..query.grammars import SQLiteGrammar
from ..schema.platforms import SQLitePlatform


class SQLiteConnector:

    name = "sqlite"

    def get_connection(self):
        return SQLiteConnection

    def get_grammar(self):
        return SQLiteGrammar

    def get_platform(self):
        return SQLitePlatform
