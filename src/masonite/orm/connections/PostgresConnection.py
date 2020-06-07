import random

from ..exceptions import DriverNotFound
from .BaseConnection import BaseConnection

CONNECTION_POOL = []


class PostgresConnection(BaseConnection):
    """Postgres Connection class.
    """

    name = "postgres"

    def make_connection(self):
        """This sets the connection on the connection class
        """
        try:
            import psycopg2
        except ModuleNotFoundError:
            raise DriverNotFound(
                "You must have the 'psycopg2' package installed to make a connection to Postgres. Please install it using 'pip install psycopg2-binary'"
            )

        self._connection = psycopg2.connect(**self.get_connection_details())

        return self

    def get_connection_details(self):
        """This is responsible for standardizing the normal connection
        details and passing it into the connection.

        This will eventually be unpacked so make sure the keys are the same as the keywords
        that should pass to your connection method
        """
        connection_details = {}
        connection_details.setdefault("host", self.connection_details.get("host"))
        connection_details.setdefault("user", self.connection_details.get("user"))
        connection_details.setdefault(
            "password", self.connection_details.get("password")
        )
        connection_details.setdefault("port", int(self.connection_details.get("port")))
        connection_details.setdefault("dbname", self.connection_details.get("database"))
        connection_details.update(self.connection_details.get("options", {}))
        return connection_details

    @classmethod
    def get_database_name(self):
        return self().get_connection_details().get("db")

    def reconnect(self):
        pass

    def commit(self):
        """Transaction
        """
        return self._connection.commit()

    def begin(self):
        """Transaction
        """
        return self._connection.begin()

    def rollback(self):
        """Transaction
        """
        self._connection.rollback()

    def transaction_level(self):
        """Transaction
        """
        pass

    def query(self, query, bindings=(), results="*"):
        """Make the actual query that will reach the database and come back with a result.

        Arguments:
            query {string} -- A string query. This could be a qmarked string or a regular query.
            bindings {tuple} -- A tuple of bindings

        Keyword Arguments:
            results {str|1} -- If the results is equal to an asterisks it will call 'fetchAll'
                    else it will return 'fetchOne' and return a single record. (default: {"*"})

        Returns:
            dict|None -- Returns a dictionary of results or None
        """
        import psycopg2

        query = query.replace("'?'", "%s")
        print("running query:", query, bindings)
        if self._dry:
            return {}
        try:
            if self._connection.closed:
                self.make_connection()
            with self._connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            ) as cursor:
                cursor.execute(query, bindings)
                if results == 1:
                    return dict(cursor.fetchone() or {})
                else:
                    if "SELECT" in cursor.statusmessage:
                        return cursor.fetchall()
                    return {}
        except Exception as e:
            raise e
        finally:
            self._connection.close()
