from ..connections.ConnectionFactory import ConnectionFactory
from ..builder.QueryBuilder import QueryBuilder
from ..grammar.mysql_grammar import MySQLGrammar


class Model:

    __fillable__ = []
    __guarded__ = ["*"]
    __table__ = "users"
    __connection__ = "default"
    __resolved_connection__ = None

    _booted = False

    @classmethod
    def boot(cls):

        if not cls._booted:
            cls.__resolved_connection__ = ConnectionFactory().make(cls.__connection__)
            cls.builder = QueryBuilder(
                MySQLGrammar, cls.__resolved_connection__, table=cls.__table__
            )
            cls.builder.set_action("select")
            cls._booted = True
            cls._boot_parent_scopes(cls)

    def _boot_parent_scopes(cls):
        for parent in cls.__bases__:
            cls.apply_scope(parent)

    @classmethod
    def apply_scope(cls, scope_class):
        cls.boot()
        boot_methods = [ v for k,v in scope_class.__dict__.items() if k.startswith('boot_')]
        for method in boot_methods:
            method(cls, cls.builder)
        
        return cls

    @classmethod
    def first(cls):
        return cls.builder.first()

    @classmethod
    def all(cls):
        cls.boot()
        return cls.builder.set_action("select").all()

    @classmethod
    def find(cls, record_id):
        cls._boot_if_not_booted()
        return cls.builder.where("id", record_id).first()

    @classmethod
    def _boot_if_not_booted(cls):
        if not cls._booted:
            cls.boot()

        return cls

    def first_or_new(self):
        pass

    def first_or_create(self):
        pass

    @classmethod
    def where(cls, *args, **kwargs):
        cls.boot()
        return cls.builder.where(*args, **kwargs)

    @classmethod
    def limit(cls, *args, **kwargs):
        cls.boot()
        return cls.builder.limit(*args, **kwargs)

    def select(self):
        pass

    def hydrate(self):
        pass

    def fill(self):
        pass

    def create(self):
        pass

    def delete(self):
        pass

    def get(self):
        pass

    def find_or_fail(self):
        pass

    def update_or_create(self):
        pass

    def touch(self):
        pass

    @staticmethod
    def set_connection_resolver(self):
        pass
