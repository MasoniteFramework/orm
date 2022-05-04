class DriverNotFound(Exception):
    pass


class ModelNotFound(Exception):
    pass


class HTTP404(Exception):
    pass


class ConnectionNotRegistered(Exception):
    pass


class QueryException(Exception):
    pass


class MigrationNotFound(Exception):
    pass


class ConfigurationNotFound(Exception):
    pass


class InvalidUrlConfiguration(Exception):
    pass


class MultipleRecordsFound(Exception):
    pass
