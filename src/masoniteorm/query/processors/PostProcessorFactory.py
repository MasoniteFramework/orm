from .SQLitePostProcessor import SQLitePostProcessor
from .MySQLPostProcessor import MySQLPostProcessor
from .PostgresPostProcessor import PostgresPostProcessor
from .MSSQLPostProcessor import MSSQLPostProcessor


class PostProcessorFactory:

    processors = {
        "sqlite": SQLitePostProcessor,
        "mysql": MySQLPostProcessor,
        "postgres": PostgresPostProcessor,
        "mssql": MSSQLPostProcessor
    }

    def make(self, processor):
        return self.processors[processor]
