from contextlib import ContextDecorator
from config.database import db


class Transaction(ContextDecorator):

    def __init__(self, using, connection="default"):
        self.using = using
        self.connection = connection

    def __enter__(self):
        builder = db.get_query_builder(self.connection)
        builder.begin()
        return builder

    def __exit__(self, exc_type, exc_value, traceback):
        import pdb ; pdb.set_trace()
        if exc_value:
            db.rollback(self.connection)
        else:
            db.commit(self.connection)
        return True


def transaction(using=None, connection="default"):
    """Function allowing to use the class as a context manager or a decorator.
    @transaction(...) or context manager: with transaction(...)
    """
    if callable(using):
        return Transaction(connection)(using)
    else:
        return Transaction(connection, using)
