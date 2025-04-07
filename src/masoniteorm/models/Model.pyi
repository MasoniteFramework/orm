from typing import Any, Callable, Dict

from ..query.QueryBuilder import QueryBuilder

class Model:
    @classmethod
    def get_primary_key(cls):
        """Gets the primary key column

        Returns:
            mixed
        """
        pass

    @classmethod
    def get_columns(cls):
        pass

    @classmethod
    def get_table_name(cls):
        """Gets the table name.

        Returns:
            str
        """
        pass

    @classmethod
    def table(cls, table):
        """Gets the table name.

        Returns:
            str
        """
        pass

    @classmethod
    def find(cls, record_id, query=False):
        """Finds a row by the primary key ID.

        Arguments:
            record_id {int} -- The ID of the primary key to fetch.

        Returns:
            Model
        """
        pass

    @classmethod
    def find_or_fail(cls, record_id, query=False):
        """Finds a row by the primary key ID or raise a ModelNotFound exception.

        Arguments:
            record_id {int} -- The ID of the primary key to fetch.

        Returns:
            Model
        """
        pass

    @classmethod
    def hydrate(cls, result, relations=None):
        """Takes a result and loads it into a model

        Args:
            result ([type]): [description]
            relations (dict, optional): [description]. Defaults to {}.

        Returns:
            [type]: [description]
        """
        pass

    @classmethod
    def new_collection(cls, data):
        """Takes a result and puts it into a new collection.
        This is designed to be able to be overidden by the user.

        Args:
            data (list|dict): Could be any data type but will be loaded directly into a collection.

        Returns:
            Collection
        """
        pass

    @classmethod
    def create(cls, dictionary=None, query=False, cast=True, **kwargs):
        """Creates new records based off of a dictionary as well as data set on the model
        such as fillable values.

        Args:
            dictionary (dict, optional): [description]. Defaults to {}.
            query (bool, optional): [description]. Defaults to False.
            cast (bool, optional): [description]. Whether or not to cast passed values.

        Returns:
            self: A hydrated version of a model
        """
        pass

    @classmethod
    def filter_fillable(cls, dictionary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filters provided dictionary to only include fields specified in the model's __fillable__ property

        Passed dictionary is not mutated.
        """
        pass

    @classmethod
    def filter_mass_assignment(
        cls, dictionary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Filters the provided dictionary in preparation for a mass-assignment operation

        Wrapper around filter_fillable() & filter_guarded(). Passed dictionary is not mutated.
        """
        pass

    @classmethod
    def filter_guarded(cls, dictionary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filters provided dictionary to exclude fields specified in the model's __guarded__ property

        Passed dictionary is not mutated.
        """
        pass

    @classmethod
    def first_or_create(cls, wheres, creates: dict = None):
        """Get the first record matching the attributes or create it.

        Returns:
            Model
        """
        pass

    @classmethod
    def update_or_create(cls, wheres, updates):
        pass

    @classmethod
    def load(cls, *loads):
        pass

    def add_select(self, alias, callable):
        """Specifies columns that should be selected

        Returns:
            self
        """
        pass

    def find_or(
        self, record_id: int, callback: Callable, args=None, column=None
    ):
        """Finds a row by the primary key ID (Requires a model) or raise a ModelNotFound exception.

        Arguments:
            record_id {int} -- The ID of the primary key to fetch.
            callback {Callable} -- The function to call if no record is found.

        Returns:
            Model|Callable
        """
        pass

    def get_primary_key_type(self):
        """Gets the primary key column type

        Returns:
            mixed
        """
        pass

    def get_primary_key_value(self):
        """Gets the primary key value.

        Raises:
            AttributeError: Raises attribute error if the model does not have an
                attribute with the primary key.

        Returns:
            str|int
        """
        pass

    def get_foreign_key(self):
        """Gets the foreign key based on this model name.

        Args:
            relationship (str): The relationship name.

        Returns:
            str
        """
        pass

    def query(self):
        pass

    def get_builder(self):
        pass

    def get_selects(self):
        pass

    def get_connection_details(self):
        pass

    def boot(self):
        pass

    def append_passthrough(self, passthrough):
        pass

    def is_loaded(self):
        pass

    def is_created(self):
        pass

    def add_relation(self, relations):
        pass

    def fill(self, attributes):
        pass

    def fill_original(self, attributes):
        pass

    def cast_value(self, attribute: str, value: Any):
        """
        Given an attribute name and a value, casts the value using the model's registered caster.
        If no registered caster exists, returns the unmodified value.
        """
        pass

    def cast_values(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs provided dictionary through all model casters and returns the result.

        Does not mutate the passed dictionary.
        """
        pass

    def fresh(self):
        pass

    def serialize(self, exclude=None, include=None):
        """Takes the data as a model and converts it into a dictionary.

        Returns:
            dict
        """
        pass

    def to_json(self):
        """Converts a model to JSON

        Returns:
            string
        """
        pass

    def relations_to_dict(self):
        """Converts a models relationships to a dictionary

        Returns:
            [type]: [description]
        """
        pass

    def touch(self, date=None, query=True):
        """Updates the current timestamps on the model"""

        pass

    def only(self, attributes: list) -> dict:
        pass

    def get_raw_attribute(self, attribute):
        """Gets an attribute without having to call the models magic methods. Gets around infinite recursion loops.

        Args:
            attribute (string): The attribute to fetch

        Returns:
            mixed: Any value an attribute can be.
        """
        pass

    def is_dirty(self):
        pass

    def get_original(self, key):
        pass

    def get_dirty(self, key):
        pass

    def get_dirty_keys(self):
        pass

    def save(self, query=False):
        pass

    def get_value(self, attribute):
        pass

    def get_dirty_value(self, attribute):
        pass

    def all_attributes(self):
        pass

    def delete_attribute(self, key):
        pass

    def get_dirty_attributes(self):
        pass

    def get_dates(self):
        """
        Get the attributes that should be converted to dates.

        :rtype: list
        """
        pass

    def get_new_date(self, _datetime=None):
        """
        Get the attributes that should be converted to dates.

        :rtype: list
        """
        pass

    def get_new_datetime_string(self, _datetime=None):
        """
        Given an optional datetime value, constructs and returns a new datetime string.
        If no datetime is specified, returns the current time.

        :rtype: list
        """
        pass

    def get_new_serialized_date(self, _datetime):
        """
        Get the attributes that should be converted to dates.

        :rtype: list
        """
        pass

    def set_appends(self, appends):
        """
        Get the attributes that should be converted to dates.

        :rtype: list
        """
        pass

    def save_many(self, relation, relating_records):
        pass

    def detach_many(self, relation, relating_records):
        pass

    def related(self, relation):
        pass

    def get_related(self, relation):
        pass

    def attach(self, relation, related_record):
        pass

    def detach(self, relation, related_record):
        pass

    def save_quietly(self):
        """This method calls the save method on a model without firing the saved & saving observer events. Saved/Saving
        are toggled back on once save_quietly has been ran.

        Instead of calling:

        User().save(...)

        you can use this:

        User.save_quietly(...)
        """
        pass

    def delete_quietly(self):
        """This method calls the delete method on a model without firing the delete & deleting observer events.
        Instead of calling:

        User().delete(...)

        you can use this:

        User.delete_quietly(...)

        Returns:
            self
        """
        pass

    def attach_related(self, relation, related_record):
        pass
    # =====================================================

    def add_select(self, alias: str, callable: Any):
        """Specifies a select subquery."""
        pass

    def aggregate(self, aggregate: str, column: str, alias: str):
        """Helper function to aggregate.

        Arguments:
            aggregate {string} -- The name of the aggregation.
            column {string} -- The name of the column to aggregate.
        """

    def all(self, selects: list = [], query: bool = False):
        """Returns all records from the table.

        Returns:
            dictionary -- Returns a dictionary of results.
        """
        pass

    def get(self, selects: list = []):
        """Runs the select query built from the query builder.

        Returns:
            self
        """
        pass

    def avg(self, column: str):
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        pass

    def between(self, column: str, low: str | int, high: str | int):
        """Specifies a where between expression.

        Arguments:
            column {string} -- The name of the column.
            low {string} -- The value on the low end.
            high {string} -- The value on the high end.

        Returns:
            self
        """
        pass

    def bulk_create(self, creates: list[dict], query: bool = False, cast=True):
        pass

    def chunk(self, chunk_amount: str | int):
        pass

    def count(self, column: str = None):
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        pass

    def decrement(self, column: str, value: int = 1):
        """Decrements a column's value.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            value {int} -- The value to decrement by. (default: {1})

        Returns:
            self
        """
        pass

    def delete(
        self, column: str = None, value: str = None, query: bool = False
    ):
        """Specify the column and value to delete
        or deletes everything based on a previously used where expression.

        Keyword Arguments:
            column {string} -- The name of the column (default: {None})
            value {string|int} -- The value of the column (default: {None})

        Returns:
            self
        """
        pass

    def distinct(self, boolean: bool = True):
        """Species that the select query should be a SELECT DISTINCT query."""
        pass

    def doesnt_exist(self) -> bool:
        """Determines if any rows exist for the current query.

        Returns:
            Bool - True or False
        """
        pass

    def doesnt_have(self) -> bool:
        """Determine if any related rows exist for the current query.

        Returns:
            Bool - True or False
        """
        pass

    def where_doesnt_have(self, relationship, callback):
        pass

    def or_doesnt_have(self, *relationships):
        pass

    def exists(self) -> bool:
        """Determine if rows exist for the current query.

        Returns:
            Bool - True or False
        """
        pass

    def find_or_404(self, record_id: str | int):
        """Finds a row by the primary key ID (Requires a model) or raise an 404 exception.

        Arguments:
            record_id {int} -- The ID of the primary key to fetch.

        Returns:
            Model|HTTP404
        """
        pass

    def first_or_fail(self, query: bool = False):
        """Returns the first row from database. If no result found a ModelNotFound exception.

        Returns:
            dictionary|ModelNotFound
        """
        pass

    def first(self, fields: list = None, query: bool = False):
        """Gets the first record.

        Returns:
            dictionary -- Returns a dictionary of results.
        """
        pass

    def first_where(self, column: str, *args):
        """Gets the first record with the given key / value pair"""
        pass

    def force_update(self, updates: dict, dry: bool = False):
        pass

    def from_(self, table: str):
        """Alias for the table method

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        pass

    def from_raw(self, table: str):
        """Alias for the table method

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        pass

    def last(self, column: str = None, query: bool = False):
        """Gets the last record, ordered by column in descendant order or primary
        key if no column is given.

        Returns:
            dictionary -- Returns a dictionary of results.
        """
        pass

    def group_by_raw(self, query: str, bindings: list = None):
        """Specifies a column to group by.

        Arguments:
            query {string} -- A raw query

        Returns:
            self
        """
        pass

    def group_by(self, column: str):
        """Specifies a column to group by.

        Arguments:
            column {string} -- The name of the column to group by.

        Returns:
            self
        """
        pass

    def has(self, *relationships: str):
        pass

    def or_has(self, *relationships):
        pass

    def having(self, column, equality="", value=""):
        """Specifying a having expression.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            equality {string} -- An equality operator (default: {"="})
            value {string} -- The value of the having expression (default: {""})

        Returns:
            self
        """
        pass

    def having_raw(self, string: str):
        """Specifies raw SQL that should be injected into the having expression.

        Arguments:
            string {string} -- The raw query string.

        Returns:
            self
        """
        pass

    def increment(self, column: str, value: int = 1):
        """Increments a column's value.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            value {int} -- The value to increment by. (default: {1})

        Returns:
            self
        """
        pass

    def in_random_order(self):
        """Puts Query results in random order"""
        pass

    def join_on(
        self,
        relationship: str,
        callback: callable = None,
        clause: str = "inner",
    ):
        pass

    def join(
        self,
        table: str,
        column1: str = None,
        equality: str = None,
        column2: str = None,
        clause: str = "inner",
    ):
        """Specifies a join expression.

        Arguments:
            table {string} -- The name of the table or an instance of JoinClause.
            column1 {string} -- The name of the foreign table.
            equality {string} -- The equality to join on.
            column2 {string} -- The name of the local column.

        Keyword Arguments:
            clause {string} -- The action clause. (default: {"inner"})

        Returns:
            self
        """
        pass

    def joins(self, *relationships: list[str], clause: str = "inner"):
        pass

    def left_join(
        self,
        table: str,
        column1: str = None,
        equality: str = None,
        column2: str = None,
    ):
        """A helper method to add a left join expression.

        Arguments:
            table {string} -- The name of the table to join on.
            column1 {string} -- The name of the foreign table.
            equality {string} -- The equality to join on.
            column2 {string} -- The name of the local column.

        Returns:
            self
        """
        pass

    def limit(self, amount: int):
        """Specifies a limit expression.

        Arguments:
            amount {int} -- The number of rows to limit.

        Returns:
            self
        """
        pass

    def lock_for_update(self):
        pass

    def make_lock(self, lock: bool):
        pass

    def max(self, column: str):
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        pass

    def min(self, column: str):
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        pass

    def new_from_builder(self, from_builder: QueryBuilder = None):
        """Creates a new QueryBuilder class.

        Returns:
            QueryBuilder -- The ORM QueryBuilder class.
        """
        pass

    def new(self):
        """Creates a new QueryBuilder class.

        Returns:
            QueryBuilder -- The ORM QueryBuilder class.
        """
        pass

    def not_between(self, column: str, low: str | int, high: str | int):
        """Specifies a where not between expression.

        Arguments:
            column {string} -- The name of the column.
            low {string} -- The value on the low end.
            high {string} -- The value on the high end.

        Returns:
            self
        """
        pass

    def offset(self, amount: int):
        """Specifies an offset expression.

        Arguments:
            amount {int} -- The number of rows to limit.

        Returns:
            self
        """
        pass

    def on(self, connection: str):
        pass

    def or_where(self, column: str | int, *args) -> QueryBuilder:
        """Specifies an or where query expression.

        Arguments:
            column {[type]} -- [description]
            value {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        pass

    def or_where_null(self, column: str):
        """Specifies a where expression where the column is NULL.

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        pass

    def or_where_exists(self, value: "str|int|QueryBuilder"):
        """Specifies a where exists expression.

        Arguments:
            value {string|int|QueryBuilder} -- A value to check for the existence of a query expression.

        Returns:
            self
        """
        pass

    def or_where_not_exists(self, value: "str|int|QueryBuilder"):
        """Specifies a where exists expression.

        Arguments:
            value {string|int|QueryBuilder} -- A value to check for the existence of a query expression.

        Returns:
            self
        """
        pass

    def or_where_has(self, relationship, callback):
        pass

    def or_where_doesnt_have(self, relationship, callback):
        pass

    def order_by_raw(self, query: str, bindings: list = None):
        """Specifies a column to order by.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            direction {string} -- Specify either ASC or DESC order. (default: {"ASC"})

        Returns:
            self
        """
        pass

    def order_by(self, column: str, direction: str = "ASC|DESC"):
        """Specifies a column to order by.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            direction {string} -- Specify either ASC or DESC order. (default: {"ASC"})

        Returns:
            self
        """
        pass

    def paginate(self, per_page: int, page: int = 1):
        pass

    def right_join(
        self,
        table: str,
        column1: str = None,
        equality: str = None,
        column2: str = None,
    ):
        """A helper method to add a right join expression.

        Arguments:
            table {string} -- The name of the table to join on.
            column1 {string} -- The name of the foreign table.
            equality {string} -- The equality to join on.
            column2 {string} -- The name of the local column.

        Returns:
            self
        """
        pass

    def select_raw(self, query: str):
        """Specifies raw SQL that should be injected into the select expression.

        Returns:
            self
        """
        pass

    def select(self, *args: str):
        """Specifies columns that should be selected

        Returns:
            self
        """
        pass

    def set_global_scope(
        self,
        name: str = "",
        callable: callable = None,
        action: str = "select",
    ):
        """Sets the global scopes that should be used before creating the SQL.

        Arguments:
            cls {masoniteorm.Model} -- An ORM model class.
            name {string} -- The name of the global scope.

        Returns:
            self
        """
        pass

    def set_schema(self, schema):
        pass

    def shared_lock(self):
        pass

    def simple_paginate(self, per_page: int, page: int = 1):
        pass

    def skip(self, *args, **kwargs):
        """Alias for limit method."""
        pass

    def statement(self, query: str, bindings: list = ()):
        pass

    def sum(self, column: str):
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        pass

    def table_raw(self, query: str):
        """Sets a query as the table

        Arguments:
            query {string} -- The query to use for the table

        Returns:
            self
        """
        pass

    def take(self, *args, **kwargs):
        """Alias for limit method"""
        pass

    def to_qmark(self) -> str:
        """Compiles the QueryBuilder class into a Qmark SQL statement.

        Returns:
            self
        """
        pass

    def to_sql(self) -> str:
        """Compiles the QueryBuilder class into a SQL statement.

        Returns:
            self
        """
        pass

    def truncate(self, foreign_keys: bool = False):
        pass

    def update(
        self,
        updates: dict,
        dry: bool = False,
        force: bool = False,
        cast: bool = True,
    ):
        """Specifies columns and values to be updated.

        Arguments:
            updates {dictionary} -- A dictionary of columns and values to update.
            dry {bool, optional} -- Whether a query should actually run
            force {bool, optional} -- Force the update even if there are no changes
            cast {bool, optional} -- Run all values through model's casters

        Returns:
            self
        """
        pass

    def when(self, conditional: bool, callback: callable):
        pass

    def where_between(self, *args, **kwargs):
        """Alias for between"""
        pass

    def where_column(self, column1: str, column2: str):
        """Specifies where two columns equal each other.

        Arguments:
            column1 {string} -- The name of the column.
            column2 {string} -- The name of the column.

        Returns:
            self
        """
        pass

    def where_date(self, column: str, date: Any):
        """Specifies a where DATE expression

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        pass

    def or_where_date(self, column: str, date: Any):
        """Specifies a where DATE expression

        Arguments:
            column {string} -- The name of the column.
            date {string|datetime|pendulum} -- The name of the column.

        Returns:
            self
        """
        pass

    def where_exists(self, value: Any):
        """Specifies a where exists expression.

        Arguments:
            value {string|int|QueryBuilder} -- A value to check for the existence of a query expression.

        Returns:
            self
        """
        pass

    def where_from_builder(self, builder: QueryBuilder):
        """Specifies a where expression.

        Arguments:
            column {string} -- The name of the column to search

        Keyword Arguments:
            args {List} -- The operator and the value of the column to search. (default: {None})

        Returns:
            self
        """
        pass

    def where_has(self, relationship: str, callback: Any):
        pass

    def where_in(self, column: str, wheres: list = None):
        """Specifies where a column contains a list of a values.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            wheres {list} -- A list of values (default: {[]})

        Returns:
            self
        """
        pass

    def where_like(self, column: str, value: str):
        """Specifies a where LIKE expression.

        Arguments:
            column {string} -- The name of the column to search
            value {string} -- The value of the column to match

        Returns:
            self
        """
        pass

    def where_not_between(self, *args: Any, **kwargs: Any):
        """Alias for not_between"""
        pass

    def where_not_in(self, column: str, wheres: list = None):
        """Specifies where a column does not contain a list of a values.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            wheres {list} -- A list of values (default: {[]})

        Returns:
            self
        """
        pass

    def where_not_like(self, column: str, value: str):
        """Specifies a where expression.

        Arguments:
            column {string} -- The name of the column to search
            value {string} -- The value of the column to match

        Returns:
            self
        """
        pass

    def where_not_null(self, column: str):
        """Specifies a where expression where the column is not NULL.

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        pass

    def where_null(self, column: str):
        """Specifies a where expression where the column is NULL.

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        pass

    def where_raw(self, query: str, bindings: tuple = ()):
        """Specifies raw SQL that should be injected into the where expression.

        Arguments:
            query {string} -- The raw query string.

        Keyword Arguments:
            bindings {tuple} -- query bindings that should be added to the connection. (default: {()})

        Returns:
            self
        """
        pass

    def without_global_scopes(self):
        pass

    def where(self, column: str, *args: Any):
        """Specifies a where expression.

        Arguments:
            column {string} -- The name of the column to search

        Keyword Arguments:
            args {List} -- The operator and the value of the column to search. (default: {None})

        Returns:
            self
        """
        pass

    def with_(self, *eagers: str):
        pass

    def with_count(self, relationship: str, callback: Any = None):
        pass

    def latest(self, *fields):
        """Gets the latest record.

        Returns:
            querybuilder
        """
        pass

    def oldest(self, *fields):
        """Gets the oldest record.

        Returns:
            querybuilder
        """
        pass

    def value(self, column: str):
        pass
