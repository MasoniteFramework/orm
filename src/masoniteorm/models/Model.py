import json
from datetime import datetime

from inflection import tableize
import inspect

from ..query import QueryBuilder
from ..collection import Collection
from ..connections import ConnectionFactory, ConnectionResolver
from ..query.grammars import MySQLGrammar
from ..scopes import BaseScope, SoftDeleteScope, SoftDeletesMixin, TimeStampsMixin

"""This is a magic class that will help using models like User.first() instead of having to instatiate a class like
User().first()
"""


class ModelMeta(type):
    def __getattr__(self, attribute, *args, **kwargs):
        """This method is called between a Model and accessing a property. This is a quick and easy
        way to instantiate a class before the first method is called. This is to avoid needing
        to do this:

        User().where(..)

        and instead, with this class inherited as a meta class, we can do this:

        User.where(...)

        This class (potentially magically) instantiates the class even though we really didn't instantiate it.

        Args:
            attribute (string): The name of the attribute

        Returns:
            Model|mixed: An instantiated model's attribute
        """
        instantiated = self()
        return getattr(instantiated, attribute)


class BoolCast:
    """Casts a value to a boolean"""

    def get(self, value):
        return bool(value)


class JsonCast:
    """Casts a value to JSON"""

    def get(self, value):
        return json.dumps(value)


class Model(TimeStampsMixin, metaclass=ModelMeta):
    """The ORM Model class

    Base Classes:
        TimeStampsMixin (TimeStampsMixin): Adds scopes to add timestamps when something is inserted
        metaclass (ModelMeta, optional): Helps instantiate a class when it hasn't been instantiated. Defaults to ModelMeta.
    """

    __fillable__ = ["*"]
    __guarded__ = ["*"]
    __dry__ = False
    __table__ = None
    __connection__ = "default"
    __resolved_connection__ = None

    _booted = False
    _scopes = {}
    __primary_key__ = "id"
    __casts__ = {}
    __dates__ = []
    __hidden__ = []
    __timestamps__ = True
    __with__ = ()

    date_created_at = "created_at"
    date_updated_at = "updated_at"

    """Pass through will pass any method calls to the model directly through to the query builder.
    Anytime one of these methods are called on the model it will actually be called on the query builder class.
    """
    __passthrough__ = [
        "all",
        "first",
        "get",
        "has",
        "limit",
        "order_by",
        "select",
        "set_global_scope",
        "where_has",
        "where_in",
        "where",
        "with_",
        "update",
    ]

    __cast_map__ = {}

    __internal_cast_map__ = {
        "bool": BoolCast,
        "json": JsonCast,
    }

    def __init__(self):
        self.__attributes__ = {}
        self.__dirty_attributes__ = {}
        self._relationships = {}
        self.__appends__ = []
        self._global_scopes = {}

        self.get_builder()
        self.boot()

    @classmethod
    def get_primary_key(self):
        """Gets the primary key column

        Returns:
            mixed
        """
        return self.__primary_key__

    def get_primary_key_value(self):
        """Gets the primary key value.

        Raises:
            AttributeError: Raises attribute error if the model does not have an
                attribute with the primary key.

        Returns:
            str|int
        """
        try:
            return getattr(self, self.get_primary_key())
        except AttributeError:
            name = self.__class__.__name__
            raise AttributeError(
                f"class '{name}' has no attribute {self.get_primary_key()}. Did you set the primary key correctly on the model using the __primary_key__ attribute?"
            )

    def query(self):
        return self.builder

    def get_builder(self):
        self.__resolved_connection__ = ConnectionFactory().make(self.__connection__)
        self.builder = QueryBuilder(
            grammar=self.__resolved_connection__.get_default_query_grammar(),
            connection=self.__resolved_connection__,
            table=self.get_table_name(),
            connection_details=self.get_connection_details(),
            model=self,
            connection_driver=self.__connection__,
            scopes=self._scopes,
            dry=self.__dry__,
        )

        return self.builder

    def get_connection_details(self):
        return ConnectionResolver.get_connection_details()

    def boot(self):
        if not self._booted:
            for base_class in inspect.getmro(self.__class__):
                class_name = base_class.__name__

                if class_name.endswith("Mixin"):
                    getattr(base_class(), "boot_" + class_name)(self.builder)

            self._booted = True

    @classmethod
    def get_table_name(cls):
        """Gets the table name.

        Returns:
            str
        """
        return cls.__table__ or tableize(cls.__name__)

    @classmethod
    def find(cls, record_id):
        """Finds a row by the primary key ID.

        Arguments:
            record_id {int} -- The ID of the primary key to fetch.

        Returns:
            Model
        """

        return cls().where(cls.get_primary_key(), record_id).first()

    def first_or_new(self):
        pass

    def first_or_create(self):
        pass

    def is_loaded(self):
        return bool(self.__attributes__)

    def add_relation(self, relations):
        self._relationships.update(relations)
        return self

    @classmethod
    def hydrate(cls, result, relations={}):
        """Takes a result and loads it into a model

        Args:
            result ([type]): [description]
            relations (dict, optional): [description]. Defaults to {}.

        Returns:
            [type]: [description]
        """

        if result is None:
            return None

        if isinstance(result, (list, tuple)):
            response = []
            for element in result:
                response.append(cls.hydrate(element))
            return cls.new_collection(response)

        elif isinstance(result, dict):
            model = cls()
            dic = {}
            for key, value in result.items():
                if key in model.get_dates():
                    value = model.get_new_date(value)
                dic.update({key: value})
            model.__attributes__.update(dic or {})
            return model.add_relation(relations)
        elif hasattr(result, "serialize"):
            model = cls()
            model.__attributes__.update(result.serialize())
            return model
        else:
            model = cls()
            model.__attributes__.update(dict(result))
            return model

    @classmethod
    def new_collection(cls, data):
        """Takes a result and puts it into a new collection.
        This is designed to be able to be overidden by the user.

        Args:
            data (list|dict): Could be any data type but will be loaded directly into a collection.

        Returns:
            Collection
        """
        return Collection(data)

    def fill(self):
        pass

    @classmethod
    def create(cls, dictionary={}, query=False, **kwargs):
        """Creates new records based off of a dictionary as well as data set on the model
        such as fillable values.

        Args:
            dictionary (dict, optional): [description]. Defaults to {}.
            query (bool, optional): [description]. Defaults to False.

        Returns:
            self: A hydrated version of a model
        """
        if not dictionary:
            dictionary = kwargs

        if cls.__fillable__ != ["*"]:
            dictionary = {x: dictionary[x] for x in cls.__fillable__}

        if cls.__guarded__ != ["*"]:
            for x in cls.__guarded__:
                dictionary.pop(x)

        if query:
            return cls.builder.create(dictionary, query=True).to_sql()

        return cls.builder.create(dictionary)

    def serialize(self, serialized_dictionary={}):
        """Takes the data as a model and converts it into a dictionary

        Args:
            serialized_dictionary (dict, optional): A dictionary to start from.
            If not specified then the models attributes will be used. Defaults to {}.

        Returns:
            dict
        """
        if not serialized_dictionary:
            serialized_dictionary = self.__attributes__

        for key in self.__hidden__:
            if key in serialized_dictionary:
                serialized_dictionary.pop(key)

        for date_column in self.get_dates():
            if date_column in serialized_dictionary:
                serialized_dictionary[date_column] = self.get_new_serialized_date(
                    serialized_dictionary[date_column]
                )

        serialized_dictionary.update(self.__dirty_attributes__)

        # The builder is inside the attributes but should not be serialized
        serialized_dictionary.pop("builder")

        # Serialize relationships as well
        serialized_dictionary.update(self.relations_to_dict())

        for append in self.__appends__:
            serialized_dictionary.update({append: getattr(self, append)})

        return serialized_dictionary

    def to_json(self):
        """Converts a model to JSON

        Returns:
            string
        """
        return json.dumps(self.serialize())

    def find_or_fail(self):
        pass

    def update_or_create(self):
        pass

    def relations_to_dict(self):
        """Converts a models relationships to a dictionary

        Returns:
            [type]: [description]
        """
        new_dic = {}
        for key, value in self._relationships.items():
            if value == {}:
                new_dic.update({key: {}})
            else:
                new_dic.update({key: value.serialize()})

        return new_dic

    def touch(self, date=None, query=True):
        """Updates the current timestamps on the model"""

        if not self.__timestamps__:
            return False

        self._update_timestamps(date=date)

        return self.save(query=query)

    def _update_timestamps(self, date=None):
        """Sets the updated at date to the current time or a specified date

        Args:
            date (datetime.datetime, optional): a date. If none is specified then it will use the current date Defaults to None.
        """
        self.updated_at = date or self._current_timestamp()

    def _current_timestamp(self):
        return datetime.now()

    @staticmethod
    def set_connection_resolver(self):
        pass

    def __getattr__(self, attribute):
        """Magic method that is called when an attribute does not exist on the model.

        Args:
            attribute (string): the name of the attribute being accessed or called.

        Returns:
            mixed: Could be anything that a method can return.
        """

        if attribute in self.__passthrough__:

            def method(*args, **kwargs):
                return getattr(self.builder, attribute)(*args, **kwargs)

            return method

        new_name_accessor = "get_" + attribute + "_attribute"

        if (new_name_accessor) in self.__class__.__dict__:
            return self.__class__.__dict__.get(new_name_accessor)(self)

        if (
            "__attributes__" in self.__dict__
            and attribute in self.__dict__["__attributes__"]
        ):
            return self.get_value(attribute)

        if (
            "__dirty_attributes__" in self.__dict__
            and attribute in self.__dict__["__dirty_attributes__"]
        ):
            return self.get_dirty_value(attribute)

        if attribute in self.__dict__.get("_relationships", {}):
            return self.__dict__["_relationships"][attribute]

        if attribute not in self.__dict__:
            name = self.__class__.__name__

            raise AttributeError(f"class model '{name}' has no attribute {attribute}")

        return None

    def __setattr__(self, attribute, value):
        if hasattr(self, "set_" + attribute + "_attribute"):
            method = getattr(self, "set_" + attribute + "_attribute")
            value = method(value)

        try:
            if not attribute.startswith("_"):
                self.__dict__["__dirty_attributes__"].update({attribute: value})
            else:
                self.__dict__[attribute] = value
        except KeyError:
            pass

    def get_raw_attribute(self, attribute):
        """Gets an attribute without having to call the models magic methods. Gets around infinite recursion loops.

        Args:
            attribute (string): The attribute to fetch

        Returns:
            mixed: Any value an attribute can be.
        """
        return self.__attributes__.get(attribute)

    def save(self, query=False):
        builder = self.builder.where(
            self.get_primary_key(), self.get_primary_key_value()
        )

        self.__dirty_attributes__.pop("builder")

        if not query:
            return builder.update(self.__dirty_attributes__)

        return builder.update(self.__dirty_attributes__, dry=True).to_sql()

    def get_value(self, attribute):
        if attribute in self.__casts__:
            return self._cast_attribute(attribute)

        return self.__attributes__[attribute]

    def get_dirty_value(self, attribute):
        if attribute in self.__casts__:
            return self._cast_attribute(attribute)

        return self.__dirty_attributes__[attribute]

    def get_cast_map(self):
        cast_map = self.__internal_cast_map__
        cast_map.update(self.__cast_map__)
        return cast_map

    def _cast_attribute(self, attribute):
        cast_method = self.__casts__[attribute]
        cast_map = self.get_cast_map()

        if isinstance(cast_method, str):
            return cast_map[cast_method]().get(attribute)

        return cast_method(attribute)

    @classmethod
    def load(cls, *loads):
        cls.boot()
        cls._loads += loads
        return cls.builder

    def __getitem__(self, attribute):
        return getattr(self, attribute)

    def get_dates(self):
        """
        Get the attributes that should be converted to dates.

        :rtype: list
        """
        defaults = [self.date_created_at, self.date_updated_at]

        return self.__dates__ + defaults

    def get_new_date(self, datetime=None):
        """
        Get the attributes that should be converted to dates.

        :rtype: list
        """
        import pendulum

        if not datetime:
            return pendulum.now()

        if isinstance(datetime, str):
            return pendulum.parse(datetime)

        return pendulum.instance(datetime)

    def get_new_serialized_date(self, datetime):
        """
        Get the attributes that should be converted to dates.

        :rtype: list
        """
        return self.get_new_date(datetime).isoformat()

    def set_appends(self, appends):
        """
        Get the attributes that should be converted to dates.

        :rtype: list
        """
        self.__appends__ += appends
        return self
