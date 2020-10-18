from ..connections import PostgresConnection
from ..query.grammars import PostgresGrammar
from ..schema.platforms import PostgresPlatform

class PostgresConnector:

    name = "postgres"
    
    
    def get_connection(self):
        return PostgresConnection
    
    def get_grammar(self):
        return PostgresGrammar
    
    def get_platform(self):
        return PostgresPlatform