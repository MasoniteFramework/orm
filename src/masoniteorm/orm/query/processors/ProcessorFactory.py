from .SQLiteProcessor import SQLiteProcessor
from .MySQLProcessor import MySQLProcessor
from .PostgresProcessor import PostgresProcessor


class ProcessorFactory:

    processors = {
        "sqlite": SQLiteProcessor,
        "mysql": MySQLProcessor,
        "postgres": PostgresProcessor,
    }

    def make(self, processor):
        return self.processors[processor]
