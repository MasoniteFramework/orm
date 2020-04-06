from ..connections.ConnectionFactory import ConnectionFactory
from ..builder import QueryBuilder
from ..grammar.mysql_grammar import MySQLGrammar
from ..collection.Collection import Collection
import json
from datetime import datetime
from inflection import tableize


class BoolCast:
    def get(self, value):
        return bool(value)


class JsonCast:
    def get(self, value):
        return json.dumps(value)


class Model:

    __fillable__ = ["*"]
    __guarded__ = ["*"]
    __table__ = None
    __connection__ = "default"
    __resolved_connection__ = None
    _eager_load = ()
    _relationships = {}
    _booted = False
    __primary_key__ = "id"
    __casts__ = {}
    __timestamps__ = True
    _global_scopes = {}

    __cast_map__ = {
        "bool": BoolCast,
        "json": JsonCast,
    }

    def __init__(self):
        self.__attributes__ = {}
        self.__dirty_attributes__ = {}
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
                global_scopes=cls._global_scopes,
            )

            cls.builder.set_action("select")
            cls._booted = True
            cast_methods = [v for k, v in cls.__dict__.items() if k.startswith("get_")]
            for cast in cast_methods:
                cls.__casts__[cast.__name__.replace("get_", "")] = cast

            # Set global scope defaults
            cls._global_scopes[cls] = {
                "select": [],
                "insert": [],
                "update": [],
                "delete": [],
            }

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
            for action in ["select", "insert", "update", "delete"]:

                cls._global_scopes[cls][action].append(method().get(action, []))

        return cls

    @classmethod
    def get_table_name(cls):
        return cls.__table__ or tableize(cls.__name__)

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
        if isinstance(dictionary, list):
            response = []
            for element in dictionary:
                response.append(element)
            return cls.new_collection(response)
        else:
            model = cls()
            model.__attributes__.update(dictionary or {})
            return model

    @classmethod
    def new_collection(cls, collection_data):
        return Collection(collection_data)

    def fill(self):
        pass

    @classmethod
    def create(cls, dictionary):
        cls.boot()
        if cls.__fillable__ != ["*"]:
            dictionary = {x: dictionary[x] for x in cls.__fillable__}
        to_sql = cls.builder.create(dictionary).to_sql()
        return to_sql

    def delete(self):
        pass

    def get(self):
        pass

    def serialize(self):
        serialized_dictionary = self.__attributes__
        serialized_dictionary.update(self.__dirty_attributes__)
        return serialized_dictionary

    def find_or_fail(self):
        pass

    def update_or_create(self):
        pass

    def touch(self, date=None, query=True):
        """
        Update the timestamps's value from model
        """
        self.boot()

        if not self.__timestamps__:
            return False

        self._update_timestamps(date=date)

        return self.save(query=query)

    def _update_timestamps(self, date=None):
        self.updated_at = date or self._current_timestamp()

    def _current_timestamp(self):
        return datetime.now()

    @staticmethod
    def set_connection_resolver(self):
        pass

    def __getattr__(self, attribute):
        if attribute in self.__dict__["__attributes__"]:
            return self.get_value(attribute)

    def __setattr__(self, attribute, value):
        try:
            if not attribute.startswith("_"):
                self.__dict__["__dirty_attributes__"].update({attribute: value})
            else:
                self.__dict__[attribute] = value
        except KeyError:
            pass

    def save(self, query=False):

        builder = self.builder.where(
            self.get_primary_key(), self.get_primary_key_value()
        )

        if not query:
            return builder.update(self.__dirty_attributes__)

        return builder.update(self.__dirty_attributes__, dry=True).to_sql()

    def get_value(self, attribute):
        if attribute in self.__casts__:
            return self._cast_attribute(attribute)

        return self.__attributes__[attribute]

    def _cast_attribute(self, attribute):
        cast_method = self.__casts__[attribute]
        if isinstance(cast_method, str):
            return self.__cast_map__[cast_method]().get(attribute)

        return cast_method(attribute)

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
