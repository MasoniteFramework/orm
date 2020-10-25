from config.database import db


def transaction(*args, **kwargs):
    """Decorator to make atomic transactions."""
    def inner(func):
        connection_name = kwargs.get("connection", None)
        if not connection_name:
            # TODO: fetch default current connection
            connection_name = ""
        import pdb ; pdb.set_trace()
        db.begin_transaction(connection_name)
        try:
            # execute query
            func()
        except:
            import pdb; pdb.set_trace()
            db.rollback(connection_name)
        db.commit(connection_name)
    return inner
