from ..connections import MySQLConnection
from ..query.grammars import MySQLGrammar
from ..schema.platforms import MySQLPlatform

class MySQLConnector:

    name = "mysql"
    
    def get_connection(self):
        return MySQLConnection
    
    def get_grammar(self):
        return MySQLGrammar
    
    def get_platform(self):
        return MySQLPlatform