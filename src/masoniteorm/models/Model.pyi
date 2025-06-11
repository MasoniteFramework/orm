from typing import Any, Callable, Dict

from ..query.QueryBuilder import QueryBuilder

class Model:

    # ==============================
    # Model Methods
    # ==============================

    def add_relation(self, relations):
        pass

    def append_passthrough(self, passthrough):
        pass

    def attach(self, relation, related_record):
        pass

    def all_attributes(self):
        pass

    def attach_related(self, relation, related_record):
        pass

    def boot(self):
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

    @classmethod
    def create(
        cls,
        dictionary=None,
        query=False,
        cast=True,
        ignore_mass_assignment: bool = False,
        **kwargs,
    ):
        """Creates new records based off of a dictionary as well as data set on the model
        such as fillable values.

        Args:
            dictionary (dict, optional): [description]. Defaults to {}.
            query (bool, optional): [description]. Defaults to False.
            cast (bool, optional): [description]. Whether to cast passed values.

        Returns:
            self: A hydrated version of a model
        """
        pass

    def delete_attribute(self, key):
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

    def detach(self, relation, related_record):
        pass

    def detach_many(self, relation, relating_records):
        pass

    def fill(self, attributes):
        pass

    def fill_original(self, attributes):
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
    def first_or_create(cls, wheres, creates: dict = None):
        """Get the first record matching the attributes or create it.

        Returns:
            Model
        """
        pass

    def fresh(self):
        pass

    def get_builder(self):
        pass

    @classmethod
    def get_columns(cls):
        pass

    def get_connection_details(self):
        pass

    def get_dates(self):
        """
        Get the attributes that should be converted to dates.

        :rtype: list
        """
        pass

    def get_dirty(self, key):
        pass

    def get_dirty_attributes(self):
        pass

    def get_dirty_keys(self):
        pass

    def get_dirty_value(self, attribute):
        pass

    def get_foreign_key(self):
        """Gets the foreign key based on this model name.

        Args:
            relationship (str): The relationship name.

        Returns:
            str
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

    def get_original(self, key):
        pass

    @classmethod
    def get_primary_key(cls):
        """Gets the primary key column

        Returns:
            mixed
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

    def get_selects(self):
        pass

    def get_raw_attribute(self, attribute):
        """Gets an attribute without having to call the models magic methods. Gets around infinite recursion loops.

        Args:
            attribute (string): The attribute to fetch

        Returns:
            mixed: Any value an attribute can be.
        """
        pass

    def get_related(self, relation):
        pass

    @classmethod
    def get_table_name(cls):
        """Gets the table name.

        Returns:
            str
        """
        pass

    def get_value(self, attribute):
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

    def is_created(self):
        pass

    def is_dirty(self):
        pass

    def is_loaded(self):
        pass

    @classmethod
    def load(cls, *loads):
        pass

    @classmethod
    def new_collection(cls, data):
        """Takes a result and puts it into a new collection.
        This is designed to be able to be overridden by the user.

        Args:
            data (list|dict): Could be any data type but will be loaded directly into a collection.

        Returns:
            Collection
        """
        pass

    def query(self):
        pass

    def related(self, relation):
        pass

    def relations_to_dict(self):
        """Converts a models relationships to a dictionary

        Returns:
            [type]: [description]
        """
        pass

    def save(self, query=False):
        pass

    def save_many(self, relation, relating_records):
        pass

    def save_quietly(self):
        """This method calls the save method on a model without firing the saved & saving observer events. Saved/Saving
        are toggled back on once save_quietly has been run.

        Instead of calling:

        User().save(...)

        you can use this:

        User.save_quietly(...)
        """
        pass

    def serialize(self, exclude=None, include=None):
        """Takes the data as a model and converts it into a dictionary.

        Returns:
            dict
        """
        pass

    def set_appends(self, appends):
        """
        Get the attributes that should be converted to dates.

        :rtype: list
        """
        pass

    @classmethod
    def table(cls, table):
        """Gets the table name.

        Returns:
            str
        """
        pass

    def to_json(self):
        """Converts a model to JSON

        Returns:
            string
        """
        pass

    def touch(self, date=None, query=True):
        """Updates the current timestamps on the model"""

        pass

    @classmethod
    def update_or_create(cls, wheres, updates):
        pass
    # ==============================
    # QueryBuilder passthrough methods
    # all marked as @classmethod for IDE
    # autocomplete to work correctly
    # ==============================

    @classmethod
    def add_select(cls, alias: str, callable: Any) -> QueryBuilder:
        """Specifies columns that should be selected

        Returns:
            self
        """
        pass

    @classmethod
    def aggregate(
        cls, aggregate: str, column: str, alias: str
    ) -> QueryBuilder:
        """Helper function to aggregate.

        Arguments:
            aggregate {string} -- The name of the aggregation.
            column {string} -- The name of the column to aggregate.
        """
        pass

    @classmethod
    def all(cls, selects: list = [], query: bool = False):
        """Returns all records from the table.

        Returns:
            dictionary -- Returns a dictionary of results.
        """
        pass

    @classmethod
    def avg(cls, column: str) -> QueryBuilder:
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        pass

    @classmethod
    def between(
        cls, column: str, low: str | int, high: str | int
    ) -> QueryBuilder:
        """Specifies a where between expression.

        Arguments:
            column {string} -- The name of the column.
            low {string} -- The value on the low end.
            high {string} -- The value on the high end.

        Returns:
            self
        """
        pass

    @classmethod
    def bulk_create(cls, creates: list[dict], query: bool = False, cast=True):
        pass

    @classmethod
    def chunk(cls, chunk_amount: str | int):
        pass

    @classmethod
    def count(cls, column: str = None):
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        pass

    @classmethod
    def decrement(cls, column: str, value: int = 1):
        """Decrements a column's value.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            value {int} -- The value to decrement by. (default: {1})

        Returns:
            self
        """
        pass

    @classmethod
    def delete(
        cls, column: str = None, value: str = None, query: bool = False
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

    @classmethod
    def distinct(cls, boolean: bool = True) -> QueryBuilder:
        """Species that the select query should be a SELECT DISTINCT query."""
        pass

    @classmethod
    def doesnt_exist(cls) -> bool:
        """Determines if any rows exist for the current query.

        Returns:
            Bool - True or False
        """
        pass

    @classmethod
    def doesnt_have(cls) -> bool:
        """Determine if any related rows exist for the current query.

        Returns:
            Bool - True or False
        """
        pass

    @classmethod
    def exists(cls) -> bool:
        """Determine if rows exist for the current query.

        Returns:
            Bool - True or False
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

    @classmethod
    def find_or_404(cls, record_id: str | int):
        """Finds a row by the primary key ID (Requires a model) or raise an 404 exception.

        Arguments:
            record_id {int} -- The ID of the primary key to fetch.

        Returns:
            Model|HTTP404
        """
        pass

    @classmethod
    def first(cls, fields: list = None, query: bool = False):
        """Gets the first record.

        Returns:
            dictionary -- Returns a dictionary of results.
        """
        pass

    @classmethod
    def first_or_fail(cls, query: bool = False):
        """Returns the first row from database. If no result found a ModelNotFound exception.

        Returns:
            dictionary|ModelNotFound
        """
        pass

    @classmethod
    def first_where(cls, column: str, *args):
        """Gets the first record with the given key / value pair"""
        pass

    @classmethod
    def force_update(cls, updates: dict, dry: bool = False):
        pass

    @classmethod
    def from_(cls, table: str) -> QueryBuilder:
        """Alias for the table method

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        pass

    @classmethod
    def from_raw(cls, table: str) -> QueryBuilder:
        """Alias for the table method

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        pass

    @classmethod
    def get(cls, selects: list = []):
        """Runs the select query built from the query builder.

        Returns:
            self
        """
        pass

    @classmethod
    def group_by_raw(cls, query: str, bindings: list = None) -> QueryBuilder:
        """Specifies a column to group by.

        Arguments:
            query {string} -- A raw query

        Returns:
            self
        """
        pass

    @classmethod
    def group_by(cls, column: str) -> QueryBuilder:
        """Specifies a column to group by.

        Arguments:
            column {string} -- The name of the column to group by.

        Returns:
            self
        """
        pass

    @classmethod
    def has(cls, *relationships: str) -> QueryBuilder:
        pass

    @classmethod
    def having(cls, column, equality="", value="") -> QueryBuilder:
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

    @classmethod
    def having_raw(cls, string: str) -> QueryBuilder:
        """Specifies raw SQL that should be injected into the having expression.

        Arguments:
            string {string} -- The raw query string.

        Returns:
            self
        """
        pass

    @classmethod
    def increment(cls, column: str, value: int = 1):
        """Increments a column's value.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            value {int} -- The value to increment by. (default: {1})

        Returns:
            self
        """
        pass

    @classmethod
    def in_random_order(cls) -> QueryBuilder:
        """Puts Query results in random order"""
        pass

    @classmethod
    def join_on(
        cls,
        relationship: str,
        callback: callable = None,
        clause: str = "inner",
    ) -> QueryBuilder:
        pass

    @classmethod
    def join(
        self,
        table: str,
        column1: str = None,
        equality: str = None,
        column2: str = None,
        clause: str = "inner",
    ) -> QueryBuilder:
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

    @classmethod
    def joins(
        cls, *relationships: list[str], clause: str = "inner"
    ) -> QueryBuilder:
        pass

    @classmethod
    def last(cls, column: str = None, query: bool = False) -> QueryBuilder:
        """Gets the last record, ordered by column in descendant order or primary
        key if no column is given.

        Returns:
            dictionary -- Returns a dictionary of results.
        """
        pass

    @classmethod
    def latest(cls, *fields):
        """Gets the latest record.

        Returns:
            querybuilder
        """
        pass

    @classmethod
    def left_join(
        cls,
        table: str,
        column1: str = None,
        equality: str = None,
        column2: str = None,
    ) -> QueryBuilder:
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

    @classmethod
    def limit(cls, amount: int) -> QueryBuilder:
        """Specifies a limit expression.

        Arguments:
            amount {int} -- The number of rows to limit.

        Returns:
            self
        """
        pass

    @classmethod
    def lock_for_update(cls) -> QueryBuilder:
        pass

    @classmethod
    def or_doesnt_have(cls, *relationships) -> QueryBuilder:
        pass

    @classmethod
    def or_has(cls, *relationships) -> QueryBuilder:
        pass

    @classmethod
    def make_lock(cls, lock: bool):
        pass

    @classmethod
    def max(cls, column: str) -> QueryBuilder:
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        pass

    @classmethod
    def min(cls, column: str) -> QueryBuilder:
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        pass

    @classmethod
    def new(cls) -> QueryBuilder:
        """Creates a new QueryBuilder class.

        Returns:
            QueryBuilder -- The ORM QueryBuilder class.
        """
        pass

    @classmethod
    def new_from_builder(
        cls, from_builder: QueryBuilder = None
    ) -> QueryBuilder:
        """Creates a new QueryBuilder class.

        Returns:
            QueryBuilder -- The ORM QueryBuilder class.
        """
        pass

    @classmethod
    def not_between(
        cls, column: str, low: str | int, high: str | int
    ) -> QueryBuilder:
        """Specifies a where not between expression.

        Arguments:
            column {string} -- The name of the column.
            low {string} -- The value on the low end.
            high {string} -- The value on the high end.

        Returns:
            self
        """
        pass

    @classmethod
    def offset(cls, amount: int) -> QueryBuilder:
        """Specifies an offset expression.

        Arguments:
            amount {int} -- The number of rows to limit.

        Returns:
            self
        """
        pass

    @classmethod
    def oldest(cls, *fields) -> QueryBuilder:
        """Gets the oldest record.

        Returns:
            querybuilder
        """
        pass

    @classmethod
    def on(cls, connection: str) -> QueryBuilder:
        pass

    @classmethod
    def only(cls, attributes: list) -> dict:
        pass

    @classmethod
    def or_where(cls, column: str | int, *args) -> QueryBuilder:
        """Specifies an or where query expression.

        Arguments:
            column {[type]} -- [description]
            value {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        pass

    @classmethod
    def or_where_null(cls, column: str) -> QueryBuilder:
        """Specifies a where expression where the column is NULL.

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        pass

    @classmethod
    def or_where_exists(cls, value: "str|int|QueryBuilder") -> QueryBuilder:
        """Specifies a where exists expression.

        Arguments:
            value {string|int|QueryBuilder} -- A value to check for the existence of a query expression.

        Returns:
            self
        """
        pass

    @classmethod
    def or_where_not_exists(
        cls, value: "str|int|QueryBuilder"
    ) -> QueryBuilder:
        """Specifies a where exists expression.

        Arguments:
            value {string|int|QueryBuilder} -- A value to check for the existence of a query expression.

        Returns:
            self
        """
        pass

    @classmethod
    def or_where_date(cls, column: str, date: Any) -> QueryBuilder:
        """Specifies a where DATE expression

        Arguments:
            column {string} -- The name of the column.
            date {string|datetime|pendulum} -- The name of the column.

        Returns:
            self
        """
        pass

    @classmethod
    def or_where_doesnt_have(cls, relationship, callback) -> QueryBuilder:
        pass

    @classmethod
    def or_where_has(cls, relationship, callback) -> QueryBuilder:
        pass

    @classmethod
    def order_by(
        cls, column: str, direction: str = "ASC|DESC"
    ) -> QueryBuilder:
        """Specifies a column to order by.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            direction {string} -- Specify either ASC or DESC order. (default: {"ASC"})

        Returns:
            self
        """
        pass

    @classmethod
    def order_by_raw(cls, query: str, bindings: list = None) -> QueryBuilder:
        """Specifies a column to order by.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            direction {string} -- Specify either ASC or DESC order. (default: {"ASC"})

        Returns:
            self
        """
        pass

    @classmethod
    def paginate(cls, per_page: int, page: int = 1):
        pass

    @classmethod
    def right_join(
        cls,
        table: str,
        column1: str = None,
        equality: str = None,
        column2: str = None,
    ) -> QueryBuilder:
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

    @classmethod
    def select(cls, *args: str) -> QueryBuilder:
        """Specifies columns that should be selected

        Returns:
            self
        """
        pass

    @classmethod
    def select_raw(cls, query: str) -> QueryBuilder:
        """Specifies raw SQL that should be injected into the select expression.

        Returns:
            self
        """
        pass

    @classmethod
    def set_global_scope(
        cls,
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

    @classmethod
    def set_schema(cls, schema):
        pass

    @classmethod
    def shared_lock(cls):
        pass

    @classmethod
    def simple_paginate(cls, per_page: int, page: int = 1) -> QueryBuilder:
        pass

    @classmethod
    def skip(cls, *args, **kwargs) -> QueryBuilder:
        """Alias for limit method."""
        pass

    @classmethod
    def statement(cls, query: str, bindings: list = ()) -> QueryBuilder:
        pass

    @classmethod
    def sum(cls, column: str) -> QueryBuilder:
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        pass

    @classmethod
    def table_raw(cls, query: str) -> QueryBuilder:
        """Sets a query as the table

        Arguments:
            query {string} -- The query to use for the table

        Returns:
            self
        """
        pass

    @classmethod
    def take(cls, *args, **kwargs) -> QueryBuilder:
        """Alias for limit method"""
        pass

    @classmethod
    def to_qmark(cls) -> str:
        """Compiles the QueryBuilder class into a Qmark SQL statement.

        Returns:
            self
        """
        pass

    @classmethod
    def to_sql(cls) -> str:
        """Compiles the QueryBuilder class into a SQL statement.

        Returns:
            self
        """
        pass

    @classmethod
    def truncate(cls, foreign_keys: bool = False) -> QueryBuilder:
        pass

    def update(
        self,
        updates: dict,
        dry: bool = False,
        force: bool = False,
        cast: bool = True,
        ignore_mass_assignment: bool = False,
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

    @classmethod
    def value(cls, column: str):
        pass

    @classmethod
    def when(cls, conditional: bool, callback: callable) -> QueryBuilder:
        pass

    @classmethod
    def where(cls, column: str, *args: Any) -> QueryBuilder:
        """Specifies a where expression.

        Arguments:
            column {string} -- The name of the column to search

        Keyword Arguments:
            args {List} -- The operator and the value of the column to search. (default: {None})

        Returns:
            self
        """
        pass

    @classmethod
    def where_between(cls, *args, **kwargs) -> QueryBuilder:
        """Alias for between"""
        pass

    @classmethod
    def where_column(cls, column1: str, column2: str) -> QueryBuilder:
        """Specifies where two columns equal each other.

        Arguments:
            column1 {string} -- The name of the column.
            column2 {string} -- The name of the column.

        Returns:
            self
        """
        pass

    @classmethod
    def where_date(cls, column: str, date: Any) -> QueryBuilder:
        """Specifies a where DATE expression

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        pass

    @classmethod
    def where_doesnt_have(cls, relationship, callback) -> QueryBuilder:
        pass

    @classmethod
    def where_exists(cls, value: Any) -> QueryBuilder:
        """Specifies a where exists expression.

        Arguments:
            value {string|int|QueryBuilder} -- A value to check for the existence of a query expression.

        Returns:
            self
        """
        pass

    @classmethod
    def where_from_builder(cls, builder: QueryBuilder) -> QueryBuilder:
        """Specifies a where expression.

        Arguments:
            column {string} -- The name of the column to search

        Keyword Arguments:
            args {List} -- The operator and the value of the column to search. (default: {None})

        Returns:
            self
        """
        pass

    @classmethod
    def where_has(cls, relationship: str, callback: Any) -> QueryBuilder:
        pass

    @classmethod
    def where_in(cls, column: str, wheres: list = None) -> QueryBuilder:
        """Specifies where a column contains a list of a values.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            wheres {list} -- A list of values (default: {[]})

        Returns:
            self
        """
        pass

    @classmethod
    def where_like(cls, column: str, value: str) -> QueryBuilder:
        """Specifies a where LIKE expression.

        Arguments:
            column {string} -- The name of the column to search
            value {string} -- The value of the column to match

        Returns:
            self
        """
        pass

    @classmethod
    def where_not_between(cls, *args: Any, **kwargs: Any) -> QueryBuilder:
        """Alias for not_between"""
        pass

    @classmethod
    def where_not_in(cls, column: str, wheres: list = None) -> QueryBuilder:
        """Specifies where a column does not contain a list of a values.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            wheres {list} -- A list of values (default: {[]})

        Returns:
            self
        """
        pass

    @classmethod
    def where_not_like(cls, column: str, value: str) -> QueryBuilder:
        """Specifies a where expression.

        Arguments:
            column {string} -- The name of the column to search
            value {string} -- The value of the column to match

        Returns:
            self
        """
        pass

    @classmethod
    def where_not_null(cls, column: str) -> QueryBuilder:
        """Specifies a where expression where the column is not NULL.

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        pass

    @classmethod
    def where_null(cls, column: str) -> QueryBuilder:
        """Specifies a where expression where the column is NULL.

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        pass

    @classmethod
    def where_raw(cls, query: str, bindings: tuple = ()) -> QueryBuilder:
        """Specifies raw SQL that should be injected into the where expression.

        Arguments:
            query {string} -- The raw query string.

        Keyword Arguments:
            bindings {tuple} -- query bindings that should be added to the connection. (default: {()})

        Returns:
            self
        """
        pass

    @classmethod
    def with_(cls, *eagers: str | list | dict) -> QueryBuilder:
        pass

    @classmethod
    def with_count(
        cls, relationship: str, callback: Any = None
    ) -> QueryBuilder:
        pass

    @classmethod
    def without_global_scopes(cls):
        pass
