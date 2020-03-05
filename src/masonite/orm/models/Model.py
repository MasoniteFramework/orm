from ..connections.ConnectionFactory import ConnectionFactory
from ..builder.QueryBuilder import QueryBuilder
from ..grammar.mysql_grammar import MySQLGrammar
from ..collection.Collection import Collection


class Model:

    __fillable__ = []
    __guarded__ = ["*"]
    __table__ = None
    __connection__ = "default"
    __resolved_connection__ = None
    _eager_load = ()
    _relationships = {}
    _booted = False
    __primary_key__ = "id"

    def __init__(self):
        self.__attributes__ = {}
        self._relationships = {}

    def get_primary_key(self):
        return self.__primary_key__

    def get_primary_key_value(self):
        return getattr(self, self.get_primary_key())

    @classmethod
    def boot(cls):

        if not cls._booted:
            cls.__resolved_connection__ = ConnectionFactory().make(cls.__connection__)
            cls.builder = QueryBuilder(
                MySQLGrammar,
                cls.__resolved_connection__,
                table=cls.get_table_name(),
                owner=cls,
            )
            cls.builder.set_action("select")
            cls._booted = True
            cls._boot_parent_scopes(cls)
            cls._loads = ()

    def _boot_parent_scopes(cls):
        for parent in cls.__bases__:
            cls.apply_scope(parent)

    @classmethod
    def apply_scope(cls, scope_class):
        cls.boot()
        boot_methods = [
            v for k, v in scope_class.__dict__.items() if k.startswith("boot_")
        ]
        for method in boot_methods:
            method(cls, cls.builder)

        return cls

    @classmethod
    def get_table_name(cls):
        if cls.__table__:
            return cls.__table__

        return cls.__name__.lower() + "s"

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

    @classmethod
    def hydrate(cls, dictionary):
        model = cls()
        model.__attributes__.update(dictionary or {})
        return model

    @classmethod
    def new_collection(cls, collection_data):
        return Collection(collection_data)

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

    def __getattr__(self, attribute):
        if attribute in self.__attributes__:
            return self.__attributes__[attribute]

    @classmethod
    def load(cls, *loads):
        cls.boot()
        cls._loads += loads
        return cls.builder

    @classmethod
    def with_(cls, *eagers):
        cls.boot()
        cls._eager_load += eagers
        return cls.builder
