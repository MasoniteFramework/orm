class ConnectionFactory:

    _connections = {
        "mysql": "",
        "mssql": "",
        "postgres": "",
        "sqlite": "",
        "oracle": "",
    }

    _default = "mysql"

    def register(self, key, connection):
        pass

    def make(self, key):
        if key == "default":
            connection = self._connections.get(self._default)
        else:
            connection = self._connections.get(key)

        if connection:
            return connection

        raise Exception("That connection does not exist")
