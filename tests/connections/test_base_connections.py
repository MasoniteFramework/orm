import unittest

from src.masoniteorm.connections import ConnectionResolver
from tests.integrations.config.database import DB


class TestDefaultBehaviorConnections(unittest.TestCase):
    def test_should_return_connection_with_enabled_logs(self):

        connection = DB.begin_transaction("dev")
        should_log_queries = connection.full_details.get("log_queries")
        DB.commit("dev")

        self.assertTrue(should_log_queries)

    def test_should_disable_log_queries_in_connection(self):

        connection = DB.begin_transaction("dev")
        connection.disable_query_log()

        should_log_queries = connection.full_details.get("log_queries")

        self.assertFalse(should_log_queries)

        connection.enable_query_log()
        should_log_queries = connection.full_details.get("log_queries")

        DB.commit("dev")

        self.assertTrue(should_log_queries)
