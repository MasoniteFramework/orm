import json
from datetime import datetime, date as datetimedate, time as datetimetime
import logging

from inflection import tableize
import inspect

from ..query import QueryBuilder
from ..collection import Collection
from ..observers import ObservesEvents
from ..scopes import TimeStampsMixin
from ..config import load_config

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

    def set(self, value):
        return bool(value)


class JsonCast:
    """Casts a value to JSON"""

    def get(self, value):
        if isinstance(value, dict) or isinstance(value, list):
            return value

        return json.loads(value)

    def set(self, value):
        return json.dumps(value)


class IntCast:
    """Casts a value to a int"""

    def get(self, value):
        return int(value)

    def set(self, value):
        return int(value)


class FloatCast:
    """Casts a value to a float"""

    def get(self, value):
        return float(value)

    def set(self, value):
        return float(value)


class Model(TimeStampsMixin, ObservesEvents, metaclass=ModelMeta):
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
    __selects__ = []

    __observers__ = {}

    _booted = False
    _scopes = {}
    __primary_key__ = "id"
    __casts__ = {}
    __dates__ = []
    __hidden__ = []
    __relationship_hidden__ = {}
    __visible__ = []
    __timestamps__ = True
    __timezone__ = "UTC"
    __with__ = ()
    __force_update__ = False

    date_created_at = "created_at"
    date_updated_at = "updated_at"

    """Pass through will pass any method calls to the model directly through to the query builder.
    Anytime one of these methods are called on the model it will actually be called on the query builder class.
    """
    __passthrough__ = [
        "add_select",
        "aggregate",
        "all",
        "avg",
        "between",
        "bulk_create",
        "chunk",
        "count",
        "decrement",
        "delete",
        "find_or_404",
        "find_or_fail",
        "first_or_fail",
        "first",
        "force_update",
        "from_",
        "from_raw",
        "get",
        "group_by_raw",
        "group_by",
        "has",
        "having",
        "increment",
        "join_on",
        "join",
        "joins",
        "last",
        "left_join",
        "limit",
        "lock_for_update",
        "make_lock",
        "max",
        "min",
        "new_from_builder",
        "new",
        "not_between",
        "offset",
        "on",
        "or_where",
        "order_by_raw",
        "order_by",
        "paginate",
        "right_join",
        "select_raw",
        "select",
        "set_global_scope",
        "shared_lock",
        "simple_paginate",
        "skip",
        "statement",
        "sum",
        "table_raw",
        "take",
        "to_qmark",
        "to_sql",
        "truncate",
        "update",
        "when",
        "where_between",
        "where_column",
        "where_exists",
        "where_from_builder",
        "where_has",
        "where_in",
        "where_like",
        "where_not_between",
        "where_not_in",
        "where_not_like",
        "where_not_null",
        "where_null",
        "where_raw",
        "without_global_scopes",
        "where",
        "with_",
        "with_count",
    ]

    __cast_map__ = {}

    __internal_cast_map__ = {
        "bool": BoolCast,
        "json": JsonCast,
        "int": IntCast,
        "float": FloatCast,
    }

    def __init__(self):
        self.__attributes__ = {}
        self.__original_attributes__ = {}
        self.__dirty_attributes__ = {}
        if not hasattr(self, "__appends__"):
            self.__appends__ = []
        self._relationships = {}
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
        return self.get_builder()

    def get_builder(self):
        if hasattr(self, "builder"):
            return self.builder
        self.builder = QueryBuilder(
            connection=self.__connection__,
            table=self.get_table_name(),
            connection_details=self.get_connection_details(),
            model=self,
            scopes=self._scopes,
            dry=self.__dry__,
        )

        return self.builder.select(*self.__selects__)

    def get_connection_details(self):
        DB = load_config().DB
        return DB.get_connection_details()

    def boot(self):
        if not self._booted:
            self.observe_events(self, "booting")
            for base_class in inspect.getmro(self.__class__):
                class_name = base_class.__name__

                if class_name.endswith("Mixin"):
                    getattr(base_class(), "boot_" + class_name)(self.builder)

            self._booted = True
            self.observe_events(self, "booted")

            self.append_passthrough(list(self.builder._macros.keys()))

    def append_passthrough(self, passthrough):
        self.__passthrough__ += passthrough
        return self

    @classmethod
    def get_table_name(cls):
        """Gets the table name.

        Returns:
            str
        """
        return cls.__table__ or tableize(cls.__name__)

    @classmethod
    def table(cls, table):
        """Gets the table name.

        Returns:
            str
        """
        cls.__table__ = table
        return cls

    @classmethod
    def find(cls, record_id, query=False):
        """Finds a row by the primary key ID.

        Arguments:
            record_id {int} -- The ID of the primary key to fetch.

        Returns:
            Model
        """
        if isinstance(record_id, (list, tuple)):
            builder = cls().where_in(cls.get_primary_key(), record_id)
        else:
            builder = cls().where(cls.get_primary_key(), record_id)

        if query:
            return builder.to_sql()
        else:
            if isinstance(record_id, (list, tuple)):
                return builder.get()

            return builder.first()

    def first_or_new(self):
        pass

    def first_or_create(self):
        pass

    def is_loaded(self):
        return bool(self.__attributes__)

    def is_created(self):
        return self.get_primary_key() in self.__attributes__

    def add_relation(self, relations):
        self._relationships.update(relations)
        return self

    @classmethod
    def hydrate(cls, result, relations=None):
        """Takes a result and loads it into a model

        Args:
            result ([type]): [description]
            relations (dict, optional): [description]. Defaults to {}.

        Returns:
            [type]: [description]
        """

        relations = relations or {}

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
                if key in model.get_dates() and value:
                    value = model.get_new_date(value)
                dic.update({key: value})

            logger = logging.getLogger("masoniteorm.models.hydrate")
            logger.setLevel(logging.INFO)
            logger.propagate = False
            logger.info(
                f"Hydrating Model {cls.__name__}",
                extra={"class_name": cls.__name__, "class_module": cls.__module__},
            )

            model.observe_events(model, "hydrating")
            model.__attributes__.update(dic or {})
            model.__original_attributes__.update(dic or {})
            model.add_relation(relations)
            model.observe_events(model, "hydrated")
            return model

        elif hasattr(result, "serialize"):
            model = cls()
            model.__attributes__.update(result.serialize())
            model.__original_attributes__.update(result.serialize())
            return model
        else:
            model = cls()
            model.observe_events(model, "hydrating")
            model.__attributes__.update(dict(result))
            model.__original_attributes__.update(dict(result))
            model.observe_events(model, "hydrated")
            return model

    def fill(self, attributes):
        self.__attributes__.update(attributes)
        self.__original_attributes__.update(attributes)
        return self

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

    @classmethod
    def create(cls, dictionary=None, query=False, **kwargs):
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
            d = {}
            for x in cls.__fillable__:
                if x in dictionary:
                    d.update({x: dictionary[x]})
            dictionary = d

        if cls.__guarded__ != ["*"]:
            for x in cls.__guarded__:
                if x in dictionary:
                    dictionary.pop(x)

        if query:
            return cls.builder.create(
                dictionary, query=True, id_key=cls.__primary_key__
            ).to_sql()

        return cls.builder.create(dictionary, id_key=cls.__primary_key__)

    def fresh(self):
        return (
            self.get_builder()
            .where(self.get_primary_key(), self.get_primary_key_value())
            .first()
        )

    def serialize(self, exclude=None, include=None):
        """Takes the data as a model and converts it into a dictionary.

        Returns:
            dict
        """
        serialized_dictionary = self.__attributes__

        # prevent using both exclude and include at the same time
        if exclude is not None and include is not None:
            raise AttributeError("Can not define both includes and exclude values.")

        if exclude is not None:
            self.__hidden__ = exclude

        if include is not None:
            self.__visible__ = include

        # prevent using both hidden and visible at the same time
        if self.__visible__ and self.__hidden__:
            raise AttributeError(
                f"class model '{self.__class__.__name__}' defines both __visible__ and __hidden__."
            )

        if self.__visible__:
            new_serialized_dictionary = {
                k: serialized_dictionary[k]
                for k in self.__visible__
                if k in serialized_dictionary
            }
            serialized_dictionary = new_serialized_dictionary
        else:
            for key in self.__hidden__:
                if key in serialized_dictionary:
                    serialized_dictionary.pop(key)

        for date_column in self.get_dates():
            if (
                date_column in serialized_dictionary
                and serialized_dictionary[date_column]
            ):
                serialized_dictionary[date_column] = self.get_new_serialized_date(
                    serialized_dictionary[date_column]
                )

        serialized_dictionary.update(self.__dirty_attributes__)

        # The builder is inside the attributes but should not be serialized
        if "builder" in serialized_dictionary:
            serialized_dictionary.pop("builder")

        # Serialize relationships as well
        serialized_dictionary.update(self.relations_to_dict())

        for append in self.__appends__:
            serialized_dictionary.update({append: getattr(self, append)})

        remove_keys = []
        for key, value in serialized_dictionary.items():

            if key in self.__hidden__:
                remove_keys.append(key)
            if hasattr(value, "serialize"):
                value = value.serialize(self.__relationship_hidden__.get(key, []))
            if isinstance(value, datetime):
                value = self.get_new_serialized_date(value)
            if key in self.__casts__:
                value = self._cast_attribute(key, value)

            serialized_dictionary.update({key: value})

        for key in remove_keys:
            serialized_dictionary.pop(key)

        return serialized_dictionary

    def to_json(self):
        """Converts a model to JSON

        Returns:
            string
        """
        return json.dumps(self.serialize())

    @classmethod
    def update_or_create(cls, wheres, updates):
        self = cls()
        record = self.where(wheres).first()
        total = {}
        total.update(updates)
        total.update(wheres)
        if not record:
            return self.create(total, id_key=cls.get_primary_key())

        return self.where(wheres).update(total)

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
                if value is None:
                    new_dic.update({key: {}})
                    continue

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

    def __getattr__(self, attribute):
        """Magic method that is called when an attribute does not exist on the model.

        Args:
            attribute (string): the name of the attribute being accessed or called.

        Returns:
            mixed: Could be anything that a method can return.
        """

        if attribute in self.__passthrough__:

            def method(*args, **kwargs):
                return getattr(self.get_builder(), attribute)(*args, **kwargs)

            return method

        new_name_accessor = "get_" + attribute + "_attribute"

        if (new_name_accessor) in self.__class__.__dict__:
            return self.__class__.__dict__.get(new_name_accessor)(self)

        if (
            "__dirty_attributes__" in self.__dict__
            and attribute in self.__dict__["__dirty_attributes__"]
        ):
            return self.get_dirty_value(attribute)

        if (
            "__attributes__" in self.__dict__
            and attribute in self.__dict__["__attributes__"]
        ):
            if attribute in self.get_dates():
                return (
                    self.get_new_date(self.get_value(attribute))
                    if self.get_value(attribute)
                    else None
                )
            return self.get_value(attribute)

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

        if attribute in self.__casts__:
            value = self._set_cast_attribute(attribute, value)

        if attribute in self.get_dates():
            value = self.get_new_datetime_string(value)

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

    def is_dirty(self):
        return bool(self.__dirty_attributes__)

    def get_original(self, key):
        return self.__original_attributes__.get(key)

    def get_dirty(self, key):
        return self.__dirty_attributes__.get(key)

    def get_dirty_keys(self):
        return list(self.get_dirty_attributes().keys())

    def save(self, query=False):
        builder = self.get_builder()

        if "builder" in self.__dirty_attributes__:
            self.__dirty_attributes__.pop("builder")

        self.observe_events(self, "saving")

        if not query:
            if self.is_loaded():
                result = builder.update(self.__dirty_attributes__)
            else:
                result = self.create(
                    self.__dirty_attributes__,
                    query=query,
                    id_key=self.get_primary_key(),
                )
            self.observe_events(self, "saved")
            self.fill(result.__attributes__)
            return result

        if self.is_loaded():
            result = builder.update(self.__dirty_attributes__, dry=query).to_sql()
        else:
            result = self.create(self.__dirty_attributes__, query=query)

        return result

    def get_value(self, attribute):
        value = self.__attributes__[attribute]
        if attribute in self.__casts__:
            return self._cast_attribute(attribute, value)

        return value

    def get_dirty_value(self, attribute):
        value = self.__dirty_attributes__[attribute]
        if attribute in self.__casts__:
            return self._cast_attribute(attribute, value)

        return value

    def all_attributes(self):
        attributes = self.__attributes__
        attributes.update(self.get_dirty_attributes())
        for key, value in attributes.items():
            if key in self.__casts__:
                attributes.update({key: self._cast_attribute(key, value)})

        return attributes

    def delete_attribute(self, key):
        if key in self.__attributes__:
            del self.__attributes__[key]
            return True

        return False

    def get_dirty_attributes(self):
        if "builder" in self.__dirty_attributes__:
            self.__dirty_attributes__.pop("builder")
        return self.__dirty_attributes__ or {}

    def get_cast_map(self):
        cast_map = self.__internal_cast_map__
        cast_map.update(self.__cast_map__)
        return cast_map

    def _cast_attribute(self, attribute, value):
        cast_method = self.__casts__[attribute]
        cast_map = self.get_cast_map()

        if value is None:
            return None

        if isinstance(cast_method, str):
            return cast_map[cast_method]().get(value)

        return cast_method(value)

    def _set_cast_attribute(self, attribute, value):
        cast_method = self.__casts__[attribute]
        cast_map = self.get_cast_map()

        if isinstance(cast_method, str):
            return cast_map[cast_method]().set(value)

        return cast_method(value)

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

    def get_new_date(self, _datetime=None):
        """
        Get the attributes that should be converted to dates.

        :rtype: list
        """
        import pendulum

        if not _datetime:
            return pendulum.now(tz=self.__timezone__)
        elif isinstance(_datetime, str):
            return pendulum.parse(_datetime, tz=self.__timezone__)
        elif isinstance(_datetime, datetime):
            return pendulum.instance(_datetime, tz=self.__timezone__)
        elif isinstance(_datetime, datetimedate):
            return pendulum.datetime(
                _datetime.year, _datetime.month, _datetime.day, tz=self.__timezone__
            )
        elif isinstance(_datetime, datetimetime):
            return pendulum.parse(
                f"{_datetime.hour}:{_datetime.minute}:{_datetime.second}",
                tz=self.__timezone__,
            )

        return pendulum.instance(_datetime, tz=self.__timezone__)

    def get_new_datetime_string(self, _datetime=None):
        """
        Get the attributes that should be converted to dates.

        :rtype: list
        """
        return self.get_new_date(_datetime).to_datetime_string()

    def get_new_serialized_date(self, _datetime):
        """
        Get the attributes that should be converted to dates.

        :rtype: list
        """
        return self.get_new_date(_datetime).isoformat()

    def set_appends(self, appends):
        """
        Get the attributes that should be converted to dates.

        :rtype: list
        """
        self.__appends__ += appends
        return self

    def save_many(self, relation, relating_records):

        if isinstance(relating_records, Model):
            raise ValueError(
                "Saving many records requires an iterable like a collection or a list of models and not a Model object. To attach a model, use the 'attach' method."
            )

        related = getattr(self.__class__, relation)
        for related_record in relating_records:
            if not related_record.is_created():
                related_record.create(related_record.all_attributes())
            else:
                related_record.save()

            related.attach_related(self, related_record)

    def detach_many(self, relation, relating_records):

        if isinstance(relating_records, Model):
            raise ValueError(
                "Detaching many records requires an iterable like a collection or a list of models and not a Model object. To detach a model, use the 'detach' method."
            )

        related = getattr(self.__class__, relation)
        for related_record in relating_records:
            if not related_record.is_created():
                related_record.create(related_record.all_attributes())
            else:
                related_record.save()

            related.detach_related(self, related_record)

    def related(self, relation):
        related = getattr(self.__class__, relation)
        return related.where(related.foreign_key, self.get_primary_key_value())

    def get_related(self, relation):
        related = getattr(self.__class__, relation)
        return related

    def attach(self, relation, related_record):
        related = getattr(self.__class__, relation)

        if not related_record.is_created():
            related_record = related_record.create(related_record.all_attributes())
        else:
            related_record.save()

        return related.attach(self, related_record)

    def detach(self, relation, related_record):
        related = getattr(self.__class__, relation)

        if not related_record.is_created():
            related_record = related_record.create(related_record.all_attributes())
        else:
            related_record.save()

        return related.detach(self, related_record)

    def attach_related(self, relation, related_record):
        related = getattr(self.__class__, relation)

        if not related_record.is_created():
            related_record = related_record.create(related_record.all_attributes())
        else:
            related_record.save()

        return related.attach_related(self, related_record)

    @classmethod
    def on(cls, connection):
        cls.__connection__ = connection
        return cls
