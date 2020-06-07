import json
from datetime import datetime

from inflection import tableize

from ..builder import QueryBuilder
from ..collection import Collection
from ..connections import ConnectionFactory
from ..grammar import MySQLGrammar


class BoolCast:
    def get(self, value):
        return bool(value)


class JsonCast:
    def get(self, value):
        return json.dumps(value)


class Model:

    __fillable__ = ["*"]
    __guarded__ = ["*"]
    __dry__ = False
    __table__ = None
    __connection__ = "default"
    __resolved_connection__ = None
    _eager_load = ()

    _registered_relationships = {}
    _booted = False
    __primary_key__ = "id"
    __casts__ = {}
    __dates__ = []
    __hidden__ = []
    __timestamps__ = True
    _global_scopes = {}
    date_created_at = "created_at"
    date_updated_at = "updated_at"

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

    @classmethod
    def boot(cls):
        if not cls._booted:
            cls.__resolved_connection__ = ConnectionFactory().make(cls.__connection__)
            cls.builder = QueryBuilder(
                cls.__resolved_connection__.get_grammar(),
                cls.__resolved_connection__,
                table=cls.get_table_name(),
                owner=cls,
                eager_loads=cls._eager_load,
                global_scopes=cls._global_scopes,
                dry=cls.__dry__,
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
        
        return cls

    def _boot_parent_scopes(cls):
        """Applies all parent scopes.
        """
        for parent in cls.__bases__:
            cls.apply_scope(parent)

    @classmethod
    def apply_scope(cls, scope_class):
        """Applies the scope to the current model.

        Arguments:
            scope_class {object} -- A scope class.

        Returns:
            cls
        """
        cls.boot()
        boot_methods = [
            v for k, v in scope_class.__dict__.items() if k.startswith("boot_")
        ]

        for method in boot_methods:
            for action, value in method().items():
                if value not in cls._global_scopes[cls][action]:
                    cls._global_scopes[cls][action].append(value)

        return cls

    @classmethod
    def get_table_name(cls):
        """Gets the table name.

        Returns:
            str
        """
        return cls.__table__ or tableize(cls.__name__)

    @classmethod
    def get_database_name(cls):
        """Gets the database name

        Returns:
            str
        """
        cls.boot()
        return cls.__resolved_connection__

    @classmethod
    def first(cls):
        """Gets the first record from the table.

        Returns:
            Model
        """
        return cls.builder.first()

    @classmethod
    def all(cls):
        """Gets all records from the table.

        Returns:
            Collection
        """
        cls.boot()
        return cls.builder.set_action("select").all()

    @classmethod
    def find(cls, record_id):
        """Finds a row by the primary key ID.

        Arguments:
            record_id {int} -- The ID of the primary key to fetch.

        Returns:
            Model
        """
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
        """Specify a where clause.

        Returns:
            Builder
        """
        cls.boot()
        return cls.builder.where(*args, **kwargs)

    @classmethod
    def order_by(cls, *args, **kwargs):
        """Specify an order by clause.

        Returns:
            Builder
        """
        cls.boot()
        return cls.builder.order_by(*args, **kwargs)

    @classmethod
    def where_in(cls, *args, **kwargs):
        """Specify a where in clause.

        Returns:
            Builder
        """
        cls.boot()
        return cls.builder.where(*args, **kwargs)

    @classmethod
    def has(cls, *has_relationships, **kwargs):
        """Creates a clause that checks the existance of a relationship.

        Returns:
            Builder
        """
        cls.boot()
        for has_relationship in has_relationships:
            if "." in has_relationship:
                # Get nested relationship
                last_builder = cls.builder
                for split_has_relationship in has_relationship.split("."):
                    local_key = cls._registered_relationships[last_builder.owner][
                        split_has_relationship
                    ]["local"]
                    foreign_key = cls._registered_relationships[last_builder.owner][
                        split_has_relationship
                    ]["foreign"]
                    relationship = last_builder.get_relation(split_has_relationship)()

                    last_builder.where_exists(
                        relationship.where_column(
                            f"{relationship.get_table_name()}.{foreign_key}",
                            f"{last_builder.get_table_name()}.{local_key}",
                        )
                    )

                    last_builder = relationship
            else:
                relationship = getattr(cls, has_relationship)()
                local_key = cls._registered_relationships[cls][has_relationship][
                    "local"
                ]
                foreign_key = cls._registered_relationships[cls][has_relationship][
                    "foreign"
                ]
                cls.builder.where_exists(
                    relationship.where_column(
                        f"{relationship.get_table_name()}.{foreign_key}",
                        f"{cls.builder.get_table_name()}.{local_key}",
                    )
                )
        return cls.builder

    @classmethod
    def where_has(cls, has_relationship, callback):
        """Creates a clause that checks the existance of a relationship.

        Returns:
            Builder
        """
        cls.boot()
        relationship = getattr(cls, has_relationship)()

        local_key = cls._registered_relationships[cls][has_relationship]["local"]
        foreign_key = cls._registered_relationships[cls][has_relationship]["foreign"]

        callback(
            relationship.where_column(
                f"{relationship.get_table_name()}.{foreign_key}",
                f"{cls.builder.get_table_name()}.{local_key}",
            )
        )

        cls.builder.where_exists(relationship)

        return cls.builder

    @classmethod
    def limit(cls, *args, **kwargs):
        cls.boot()
        return cls.builder.limit(*args, **kwargs)

    @classmethod
    def select(cls, *args, **kwargs):
        cls.boot()
        return cls.builder.select(*args, **kwargs)

    def add_relations(self, relations):
        self._relationships.update(relations)
        return self

    @classmethod
    def hydrate(cls, dictionary, relations={}):
        if dictionary is None:
            return None

        if isinstance(dictionary, (list, tuple)):
            response = []
            for element in dictionary:
                response.append(element)
            return cls.new_collection(response)
        elif isinstance(dictionary, dict):
            model = cls()
            dic = {}
            for key, value in dictionary.items():
                if key in model.get_dates():
                    value = model.get_new_date(value)
                dic.update({key: value})
            model.__attributes__.update(dic or {})
            return model.add_relations(relations)
        elif hasattr(dictionary, "serialize"):
            model = cls()
            model.__attributes__.update(dictionary.serialize())
            return model
        else:
            model = cls()
            model.__attributes__.update(dict(dictionary))
            return model

    @classmethod
    def new_collection(cls, collection_data):
        return Collection(collection_data)

    def fill(self):
        pass

    @classmethod
    def create(cls, dictionary={}, query=False, **kwargs):
        cls.boot()
        if not dictionary:
            dictionary = kwargs

        if cls.__fillable__ != ["*"]:
            dictionary = {x: dictionary[x] for x in cls.__fillable__}

        if cls.__guarded__ != ["*"]:
            for x in cls.__guarded__:
                dictionary.pop(x)

        print(dictionary)

        if query:
            return cls.builder.create(dictionary, query=True).to_sql()

        return cls.builder.create(dictionary)

    def delete(self):
        pass

    def get(self):
        pass

    def serialize(self, serialized_dictionary={}):
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

        # Serialize relationships as well
        serialized_dictionary.update(self.relations_to_dict())

        for append in self.__appends__:
            serialized_dictionary.update({append: getattr(self, append)})

        return serialized_dictionary

    def to_json(self):
        return json.dumps(self.serialize())

    def find_or_fail(self):
        pass

    def update_or_create(self):
        pass

    def relations_to_dict(self):
        new_dic = {}
        for key, value in self._relationships.items():
            new_dic.update({key: value.serialize()})

        return new_dic

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
        if ("get_" + attribute) in self.__class__.__dict__:
            return self.__class__.__dict__.get(("get_" + attribute))(self)

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

            raise AttributeError(f"class '{name}' has no attribute {attribute}")

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
        return self.__attributes__.get(attribute)

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

    @classmethod
    def with_(cls, *eagers):
        cls.boot()
        return cls.builder.with_(eagers)

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
