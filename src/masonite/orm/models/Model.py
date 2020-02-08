from ..connections.ConnectionFactory import ConnectionFactory
from ..builder.QueryBuilder import QueryBuilder
from ..grammer.mysql_grammer import MySQLGrammer


class Model:

    __fillable__ = []
    __guarded__ = ["*"]
    __table__ = "users"
    __connection__ = "default"
    __resolved_connection__ = None

    _booted = False

    @classmethod
    def boot(cls):
        cls.__resolved_connection__ = ConnectionFactory().make(cls.__connection__)
        cls.builder = QueryBuilder(MySQLGrammer, cls.__resolved_connection__, table=cls.__table__)

    @classmethod
    def first(cls):
        return cls.builder.first()

    @classmethod
    def all(cls):
        cls.boot()
        return cls.builder.all()

    @classmethod
    def find(cls, record_id):
        return cls.builder.where('id', record_id).first()

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