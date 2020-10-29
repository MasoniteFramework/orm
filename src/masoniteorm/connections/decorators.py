from config.database import db


class Transaction(object):

    def __init__(self, connection="default"):
        self.connection = connection

    def __call__(self, fn, *args, **kwargs):
        # before function
        db.begin_transaction(self.connection)
        try:
            return fn
        except:
            db.rollback(self.connection)
        finally:
            db.commit(self.connection)
