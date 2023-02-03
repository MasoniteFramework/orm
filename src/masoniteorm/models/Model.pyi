from typing import Any, Dict

from typing_extensions import Self

from ..query.QueryBuilder import QueryBuilder

class Model:
    def add_select(alias: str, callable: Any):
        """Specifies a select subquery."""
        pass
    def aggregate(aggregate: str, column: str, alias: str):
        """Helper function to aggregate.

        Arguments:
            aggregate {string} -- The name of the aggregation.
            column {string} -- The name of the column to aggregate.
        """
    def all(selects: list = [], query: bool = False):
        """Returns all records from the table.

        Returns:
            dictionary -- Returns a dictionary of results.
        """
        pass
    def get(selects: list = []):
        """Runs the select query built from the query builder.

        Returns:
            self
        """
        pass
    def avg(column: str):
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        pass
    def between(column: str, low: str | int, high: str | int):
        """Specifies a where between expression.

        Arguments:
            column {string} -- The name of the column.
            low {string} -- The value on the low end.
            high {string} -- The value on the high end.

        Returns:
            self
        """
        pass
    def bulk_create(creates: dict, query: bool = False):
        pass
    def cast_value(attribute: str, value: Any):
        """
        Given an attribute name and a value, casts the value using the model's registered caster.
        If no registered caster exists, returns the unmodified value.
        """
        pass
    def cast_values(dictionary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs provided dictionary through all model casters and returns the result.

        Does not mutate the passed dictionary.
        """
        pass
    def chunk(chunk_amount: str | int):
        pass
    def count(column: str = None):
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        pass
    def create(
        dictionary: Dict[str, Any] = None,
        query: bool = False,
        cast: bool = False,
        **kwargs
    ):
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
    def decrement(column: str, value: int = 1):
        """Decrements a column's value.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            value {int} -- The value to decrement by. (default: {1})

        Returns:
            self
        """
    def delete(column: str = None, value: str = None, query: bool = False):
        """Specify the column and value to delete
        or deletes everything based on a previously used where expression.

        Keyword Arguments:
            column {string} -- The name of the column (default: {None})
            value {string|int} -- The value of the column (default: {None})

        Returns:
            self
        """
        pass
    def distinct(boolean: bool = True):
        """Species that the select query should be a SELECT DISTINCT query."""
        pass
    def doesnt_exist() -> bool:
        """Determines if any rows exist for the current query.

        Returns:
            Bool - True or False
        """
        pass
    def doesnt_have() -> bool:
        """Determine if any related rows exist for the current query.

        Returns:
            Bool - True or False
        """
        pass
    def exists() -> bool:
        """Determine if rows exist for the current query.

        Returns:
            Bool - True or False
        """
        pass
    def filter_fillable(dictionary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filters provided dictionary to only include fields specified in the model's __fillable__ property

        Passed dictionary is not mutated.
        """
        pass
    def filter_mass_assignment(dictionary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filters the provided dictionary in preparation for a mass-assignment operation

        Wrapper around filter_fillable() & filter_guarded(). Passed dictionary is not mutated.
        """
        pass
    def filter_guarded(dictionary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filters provided dictionary to exclude fields specified in the model's __guarded__ property

        Passed dictionary is not mutated.
        """
        pass
    def find_or_404(record_id: str | int):
        """Finds a row by the primary key ID (Requires a model) or raise an 404 exception.

        Arguments:
            record_id {int} -- The ID of the primary key to fetch.

        Returns:
            Model|HTTP404
        """
        pass
    def find(record_id: str | list) -> Self:
        """Finds a row by the primary key ID (Requires a model) or raise an 404 exception.

        Arguments:
            record_id {int} -- The ID of the primary key to fetch.

        Returns:
            Model|Collection
        """
        pass
    def find_or_fail(record_id: str | int):
        """Finds a row by the primary key ID (Requires a model) or raise a ModelNotFound exception.

        Arguments:
            record_id {int} -- The ID of the primary key to fetch.

        Returns:
            Model|ModelNotFound
        """
        pass
    def first_or_fail(query: bool = False):
        """Returns the first row from database. If no result found a ModelNotFound exception.

        Returns:
            dictionary|ModelNotFound
        """
    def first(fields: list = None, query: bool = False):
        """Gets the first record.

        Returns:
            dictionary -- Returns a dictionary of results.
        """
        pass
    def first_where(column: str, *args):
        """Gets the first record with the given key / value pair"""
        pass
    def first_or_create(wheres: dict, creates: dict = None):
        """Get the first record matching the attributes or create it.

        Returns:
            Model
        """
        pass
    def force_update(updates: dict, dry: bool = False):
        pass
    def from_(table: str):
        """Alias for the table method

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        pass
    def from_raw(table: str):
        """Alias for the table method

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        pass
    def last(column: str = None, query: bool = False):
        """Gets the last record, ordered by column in descendant order or primary
        key if no column is given.

        Returns:
            dictionary -- Returns a dictionary of results.
        """
        pass
    def group_by_raw(query: str, bindings: list = []):
        """Specifies a column to group by.

        Arguments:
            query {string} -- A raw query

        Returns:
            self
        """
        pass
    def group_by(column: str):
        """Specifies a column to group by.

        Arguments:
            column {string} -- The name of the column to group by.

        Returns:
            self
        """
        pass
    def has(*relationships: str):
        pass
    def having_raw(string: str):
        """Specifies raw SQL that should be injected into the having expression.

        Arguments:
            string {string} -- The raw query string.

        Returns:
            self
        """
        pass
    def increment(column: str, value: int = 1):
        """Increments a column's value.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            value {int} -- The value to increment by. (default: {1})

        Returns:
            self
        """
        pass
    def in_random_order():
        """Puts Query results in random order"""
        pass
    def join_on(relationship: str, callback: callable = None, clause: str = ["inner"]):
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
    def joins(*relationships: list[str], clause: str = "inner"):
        pass
    def left_join(
        table: str, column1: str = None, equality: str = None, column2: str = None
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
    def limit(amount: int):
        """Specifies a limit expression.

        Arguments:
            amount {int} -- The number of rows to limit.

        Returns:
            self
        """
        pass
    def lock_for_update():
        pass
    def make_lock(lock: bool):
        pass
    def max(column: str):
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        pass
    def min(column: str):
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        pass
    def new_from_builder(from_builder: QueryBuilder = None):
        """Creates a new QueryBuilder class.

        Returns:
            QueryBuilder -- The ORM QueryBuilder class.
        """
        pass
    def new():
        """Creates a new QueryBuilder class.

        Returns:
            QueryBuilder -- The ORM QueryBuilder class.
        """
        pass
    def not_between(column: str, low: str | int, high: str | int):
        """Specifies a where not between expression.

        Arguments:
            column {string} -- The name of the column.
            low {string} -- The value on the low end.
            high {string} -- The value on the high end.

        Returns:
            self
        """
        pass
    def offset(amount: int):
        """Specifies an offset expression.

        Arguments:
            amount {int} -- The number of rows to limit.

        Returns:
            self
        """
        pass
    def on(connection: str):
        pass
    def or_where(column: str | int, *args) -> QueryBuilder:
        """Specifies an or where query expression.

        Arguments:
            column {[type]} -- [description]
            value {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        pass
    def or_where_null(column: str):
        """Specifies a where expression where the column is NULL.

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        pass
    def order_by_raw(query: str, bindings: list = []):
        """Specifies a column to order by.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            direction {string} -- Specify either ASC or DESC order. (default: {"ASC"})

        Returns:
            self
        """
        pass
    def order_by(column: str, direction: str = "ASC|DESC"):
        """Specifies a column to order by.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            direction {string} -- Specify either ASC or DESC order. (default: {"ASC"})

        Returns:
            self
        """
        pass
    def paginate(per_page: int, page: int = 1):
        pass
    def right_join(
        table: str, column1: str = None, equality: str = None, column2: str = None
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
    def select_raw(query: str):
        """Specifies raw SQL that should be injected into the select expression.

        Returns:
            self
        """
        pass
    def select(*args: str):
        """Specifies columns that should be selected

        Returns:
            self
        """
        pass
    def set_global_scope(
        self,
        name: str = "",
        callable: callable = None,
        action: str = ["select", "update", "create", "delete"],
    ):
        """Sets the global scopes that should be used before creating the SQL.

        Arguments:
            cls {masoniteorm.Model} -- An ORM model class.
            name {string} -- The name of the global scope.

        Returns:
            self
        """
        pass
    def shared_lock():
        pass
    def simple_paginate(per_page: int, page: int = 1):
        pass
    def skip(*args, **kwargs):
        """Alias for limit method."""
        pass
    def statement(query: str, bindings: list = ()):
        pass
    def sum(column: str):
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        pass
    def table_raw(query: str):
        """Sets a query as the table

        Arguments:
            query {string} -- The query to use for the table

        Returns:
            self
        """
        pass
    def take(*args, **kwargs):
        """Alias for limit method"""
        pass
    def to_qmark() -> str:
        """Compiles the QueryBuilder class into a Qmark SQL statement.

        Returns:
            self
        """
        pass
    def to_sql() -> str:
        """Compiles the QueryBuilder class into a SQL statement.

        Returns:
            self
        """
        pass
    def truncate(foreign_keys: bool = False):
        pass
    def update(
        updates: dict, dry: bool = False, force: bool = False, cast: bool = False
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
    def when(conditional: bool, callback: callable):
        pass
    def where_between(*args, **kwargs):
        """Alias for between"""
        pass
    def where_column(column1: str, column2: str):
        """Specifies where two columns equal eachother.

        Arguments:
            column1 {string} -- The name of the column.
            column2 {string} -- The name of the column.

        Returns:
            self
        """
        pass
    def take(*args: Any, **kwargs: Any):
        """Alias for limit method"""
        pass
    def where_column(column1: str, column2: str):
        """Specifies where two columns equal eachother.

        Arguments:
            column1 {string} -- The name of the column.
            column2 {string} -- The name of the column.

        Returns:
            self
        """
        pass
    def where_date(column: str, date: Any):
        """Specifies a where DATE expression

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        pass
    def or_where_date(column: str, date: Any):
        """Specifies a where DATE expression

        Arguments:
            column {string} -- The name of the column.
            date {string|datetime|pendulum} -- The name of the column.

        Returns:
            self
        """
        pass
    def where_exists(value: Any):
        """Specifies a where exists expression.

        Arguments:
            value {string|int|QueryBuilder} -- A value to check for the existence of a query expression.

        Returns:
            self
        """
        pass
    def where_from_builder(builder: QueryBuilder):
        """Specifies a where expression.

        Arguments:
            column {string} -- The name of the column to search

        Keyword Arguments:
            args {List} -- The operator and the value of the column to search. (default: {None})

        Returns:
            self
        """
        pass
    def where_has(relationship: str, callback: Any):
        pass
    def where_in(column: str, wheres: list = []):
        """Specifies where a column contains a list of a values.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            wheres {list} -- A list of values (default: {[]})

        Returns:
            self
        """
        pass
    def where_like(column: str, value: str):
        """Specifies a where LIKE expression.

        Arguments:
            column {string} -- The name of the column to search
            value {string} -- The value of the column to match

        Returns:
            self
        """
        pass
    def where_not_between(*args: Any, **kwargs: Any):
        """Alias for not_between"""
        pass
    def where_not_in(column: str, wheres: list = []):
        """Specifies where a column does not contain a list of a values.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            wheres {list} -- A list of values (default: {[]})

        Returns:
            self
        """
        pass
    def where_not_like(column: str, value: str):
        """Specifies a where expression.

        Arguments:
            column {string} -- The name of the column to search
            value {string} -- The value of the column to match

        Returns:
            self
        """
        pass
    def where_not_null(column: str):
        """Specifies a where expression where the column is not NULL.

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        pass
    def where_null(column: str):
        """Specifies a where expression where the column is NULL.

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        pass
    def where_raw(query: str, bindings: list = []):
        """Specifies raw SQL that should be injected into the where expression.

        Arguments:
            query {string} -- The raw query string.

        Keyword Arguments:
            bindings {tuple} -- query bindings that should be added to the connection. (default: {()})

        Returns:
            self
        """
        pass
    def without_global_scopes():
        pass
    def where(column: str, *args: Any):
        """Specifies a where expression.

        Arguments:
            column {string} -- The name of the column to search

        Keyword Arguments:
            args {List} -- The operator and the value of the column to search. (default: {None})

        Returns:
            self
        """
        pass
    def with_(*eagers: str):
        pass
    def with_count(relationship: str, callback: Any = None):
        pass
