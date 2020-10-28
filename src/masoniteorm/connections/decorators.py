from config.database import db


class Transaction(object):

    def __init__(self, connection="default"):
        self.connection = connection

    def __call__(self, fn, *args, **kwargs):
        import pdb ; pdb.set_trace()
        # before function
        db.begin_transaction(self.connection)
        try:
            result = fn(*args, **kwargs)
        except:
            db.rollback(self.connection)
            return None

        # after function
        db.commit(self.connection)
        return result
