
import unittest

from src.masoniteorm.connections import ConnectionResolver
from config.database import db

class TestDefaultBehaviorConnections(unittest.TestCase):

    def test_should_return_connection_with_enabled_logs(self):
        
        connection = db.begin_transaction('sqlite')
        should_log_queries = connection.full_details.get("log_queries")  
        db.commit('sqlite')

        self.assertTrue(should_log_queries)

    def test_should_disable_log_queries_in_connection(self):
        
        connection = db.begin_transaction('sqlite')
        connection.disable_query_log()
    
        should_log_queries = connection.full_details.get("log_queries")  

        self.assertFalse(should_log_queries)

        connection.enable_query_log()
        should_log_queries = connection.full_details.get("log_queries")  

        db.commit('sqlite')
        
        self.assertTrue(should_log_queries)
