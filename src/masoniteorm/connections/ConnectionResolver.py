class ConnectionResolver:

    _connection_details = {}

    @classmethod
    def set_connection_details(cls, connection_details):
        cls._connection_details = connection_details

    @classmethod
    def get_connection_details(cls):
        return cls._connection_details
