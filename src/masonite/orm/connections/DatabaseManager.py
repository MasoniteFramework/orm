from .ConnectionFactory import ConnectionFactory


class Resolver:
    """Resolves and switches database connections on the fly
    """

    def __init__(self, connections):
        self.connections = connections

    def make(self, connection):
        return ConnectionFactory.make(connection)
