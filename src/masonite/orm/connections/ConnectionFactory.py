class ConnectionFactory:

    _connections = {
        'mysql': '',
        'mssql': '',
        'postgres': '',
        'sqlite': '',
        'oracle': '',
    }

    def register(self, key, connection):
        pass

    def make(self, key):
        connection = self._connections.get(key)
        if connection:
            return connection
        
        raise Exception('That connection does not exist')
        pass