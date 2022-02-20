import inspect

from ..config import load_config
from ..collection.Collection import Collection
from ..expressions.expressions import (
    JoinClause,
    SubGroupExpression,
    SubSelectExpression,
    SelectExpression,
    BetweenExpression,
    GroupByExpression,
    AggregateExpression,
    QueryExpression,
    OrderByExpression,
    UpdateQueryExpression,
    HavingExpression,
    FromTable,
)

from ..scopes import BaseScope
from ..schema import Schema
from ..observers import ObservesEvents
from ..exceptions import ModelNotFound, HTTP404, ConnectionNotRegistered
from ..pagination import LengthAwarePaginator, SimplePaginator
from .EagerRelation import EagerRelations
from datetime import datetime, date as datetimedate, time as datetimetime
import pendulum


class QueryBuilder(ObservesEvents):
    """A builder class to manage the building and creation of query expressions."""

    def __init__(
        self,
        grammar=None,
        connection="default",
        connection_class=None,
        table=None,
        connection_details=None,
        connection_driver="default",
        model=None,
        scopes=None,
        dry=False,
    ):
        """QueryBuilder initializer

        Arguments:
            grammar {masoniteorm.grammar.Grammar} -- A grammar class.

        Keyword Arguments:
            connection {masoniteorm.connection.Connection} -- A connection class (default: {None})
            table {str} -- the name of the table (default: {""})
        """
        self.grammar = grammar
        self.table(table)
        self.dry = dry
        self.connection = connection
        self.connection_class = connection_class
        self._connection = None
        self._connection_details = connection_details or {}
        self._connection_driver = connection_driver
        self._scopes = scopes or {}
        self.lock = False
        self._eager_relation = EagerRelations()
        if model:
            self._global_scopes = model._global_scopes
            if model.__with__:
                self.with_(model.__with__)
        else:
            self._global_scopes = {}

        self.builder = self

        self._columns = ()
        self._creates = {}

        self._sql = ""
        self._bindings = ()

        self._updates = ()

        self._wheres = ()
        self._order_by = ()
        self._group_by = ()
        self._joins = ()
        self._having = ()
        self._macros = {}

        self._aggregates = ()

        self._limit = False
        self._offset = False
        self._model = model
        self.set_action("select")

        if not self._connection_details:
            DB = load_config().DB
            self._connection_details = DB.get_connection_details()

        self.on(connection)

        if grammar:
            self.grammar = grammar

        if connection_class:
            self.connection_class = connection_class

    def shared_lock(self):
        return self.make_lock("share")

    def lock_for_update(self):
        return self.make_lock("update")

    def make_lock(self, lock):
        self.lock = lock
        return self

    def reset(self):
        """Resets the query builder instance so you can make multiple calls with the same builder instance"""

        self.set_action("select")

        self._updates = ()

        self._wheres = ()
        self._order_by = ()
        self._group_by = ()
        self._joins = ()
        self._having = ()

        return self

    def get_connection_information(self):
        return {
            "host": self._connection_details.get(self.connection, {}).get("host"),
            "database": self._connection_details.get(self.connection, {}).get(
                "database"
            ),
            "user": self._connection_details.get(self.connection, {}).get("user"),
            "port": self._connection_details.get(self.connection, {}).get("port"),
            "password": self._connection_details.get(self.connection, {}).get(
                "password"
            ),
            "prefix": self._connection_details.get(self.connection, {}).get("prefix"),
            "options": self._connection_details.get(self.connection, {}).get(
                "options", {}
            ),
            "full_details": self._connection_details.get(self.connection, {}),
        }

    def table(self, table, raw=False):
        """Sets a table on the query builder

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        if table:
            self._table = FromTable(table, raw=raw)
        else:
            self._table = table
        return self

    def from_(self, table):
        """Alias for the table method

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        return self.table(table)

    def from_raw(self, table):
        """Alias for the table method

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        return self.table(table, raw=True)

    def table_raw(self, table):
        """Sets a table on the query builder

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        return self.from_raw(table)

    def get_table_name(self):
        """Sets a table on the query builder

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        return self._table.name

    def get_connection(self):
        """Sets a table on the query builder

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        return self.connection_class

    def begin(self):
        """Sets a table on the query builder

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        return self.new_connection().begin()

    def begin_transaction(self, *args, **kwargs):
        return self.begin(*args, **kwargs)

    def get_schema_builder(self):
        return Schema(connection=self.connection_class, grammar=self.grammar)

    def commit(self):
        """Sets a table on the query builder

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        return self._connection.commit()

    def rollback(self):
        """Sets a table on the query builder

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        self._connection.rollback()
        return self

    def get_relation(self, key):
        """Sets a table on the query builder

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        return getattr(self.owner, key)

    def set_scope(self, name, callable):
        """Sets a scope based on a class and maps it to a name.

        Arguments:
            cls {masoniteorm.Model} -- An ORM model class.
            name {string} -- The name of the scope to use.

        Returns:
            self
        """
        # setattr(self, name, callable)
        self._scopes.update({name: callable})

        return self

    def set_global_scope(self, name="", callable=None, action="select"):
        """Sets the global scopes that should be used before creating the SQL.

        Arguments:
            cls {masoniteorm.Model} -- An ORM model class.
            name {string} -- The name of the global scope.

        Returns:
            self
        """
        if isinstance(name, BaseScope):
            name.on_boot(self)
            return self

        if action not in self._global_scopes:
            self._global_scopes[action] = {}

        self._global_scopes[action].update({name: callable})

        return self

    def without_global_scopes(self):
        self._global_scopes = {}
        return self

    def remove_global_scope(self, scope, action=None):
        """Sets the global scopes that should be used before creating the SQL.

        Arguments:
            cls {masoniteorm.Model} -- An ORM model class.
            name {string} -- The name of the global scope.

        Returns:
            self
        """
        if isinstance(scope, BaseScope):
            scope.on_remove(self)
            return self

        del self._global_scopes.get(action, {})[scope]

        return self

    def __getattr__(self, attribute):
        """Magic method for fetching query scopes.

        This method is only used when a method or attribute does not already exist.

        Arguments:
            attribute {string} -- The attribute to fetch.

        Raises:
            AttributeError: Raised when there is no attribute or scope on the builder class.

        Returns:
            self
        """
        if attribute in self._scopes:

            def method(*args, **kwargs):
                return self._scopes[attribute](self._model, self, *args, **kwargs)

            return method

        if attribute in self._macros:

            def method(*args, **kwargs):
                return self._macros[attribute](self._model, self, *args, **kwargs)

            return method

        raise AttributeError(
            "'QueryBuilder' object has no attribute '{}'".format(attribute)
        )

    def on(self, connection):
        DB = load_config().DB

        if connection == "default":
            self.connection = self._connection_details.get("default")
        else:
            self.connection = connection

        if self.connection not in self._connection_details:
            raise ConnectionNotRegistered(
                f"Could not find the '{self.connection}' connection details"
            )

        self._connection_driver = self._connection_details.get(self.connection).get(
            "driver"
        )
        self.connection_class = DB.connection_factory.make(self._connection_driver)

        self.grammar = self.connection_class.get_default_query_grammar()

        return self

    def select(self, *args):
        """Specifies columns that should be selected

        Returns:
            self
        """
        for arg in args:
            for column in arg.split(","):
                self._columns += (SelectExpression(column),)

        return self

    def add_select(self, alias, callable):
        """Specifies columns that should be selected

        Returns:
            self
        """
        builder = callable(self.new())
        self._columns += (SubGroupExpression(builder, alias=alias),)

        return self

    def statement(self, query, bindings=()):
        result = self.new_connection().query(query, bindings)
        return self.prepare_result(result)

    def select_raw(self, string):
        """Specifies raw SQL that should be injected into the select expression.

        Returns:
            self
        """
        self._columns += (SelectExpression(string, raw=True),)
        return self

    def get_processor(self):
        return self.connection_class.get_default_post_processor()()

    def bulk_create(self, creates, query=False):
        model = None
        self.set_action("bulk_create")

        self._creates = creates

        if self._model:
            model = self._model

        if query:
            return self

        if model:
            model = model.hydrate(self._creates)
        if not self.dry:
            connection = self.new_connection()
            query_result = connection.query(self.to_qmark(), self._bindings, results=1)

            processed_results = query_result or self._creates
        else:
            processed_results = self._creates

        if model:
            return model

        return processed_results

    def create(self, creates=None, query=False, id_key="id", **kwargs):
        """Specifies a dictionary that should be used to create new values.

        Arguments:
            creates {dict} -- A dictionary of columns and values.

        Returns:
            self
        """
        self._creates = {}

        if not creates:
            creates = kwargs

        model = None

        if self._model:
            model = self._model

        self.set_action("insert")
        self._creates.update(creates)

        if query:
            return self

        if model:
            model = model.hydrate(self._creates)
            self.observe_events(model, "creating")

            # if attributes were modified during model observer then we need to update the creates here
            self._creates.update(model.get_dirty_attributes())

        if not self.dry:
            connection = self.new_connection()
            query_result = connection.query(self.to_qmark(), self._bindings, results=1)

            if model:
                id_key = model.get_primary_key()

            processed_results = self.get_processor().process_insert_get_id(
                self, query_result or self._creates, id_key
            )
        else:
            processed_results = self._creates

        if model:
            model = model.fill(processed_results)
            self.observe_events(model, "created")
            return model

        return processed_results

    def delete(self, column=None, value=None, query=False):
        """Specify the column and value to delete
        or deletes everything based on a previously used where expression.

        Keyword Arguments:
            column {string} -- The name of the column (default: {None})
            value {string|int} -- The value of the column (default: {None})

        Returns:
            self
        """
        model = None
        self.set_action("delete")

        if self._model:
            model = self._model

        if column and value:
            if isinstance(value, (list, tuple)):
                self.where_in(column, value)
            else:
                self.where(column, value)

        if query:
            return self

        if model and model.is_loaded():
            self.where(model.get_primary_key(), model.get_primary_key_value())
            self.observe_events(model, "deleting")

        result = self.new_connection().query(self.to_qmark(), self._bindings)

        if model:
            self.observe_events(model, "deleted")

        return result

    def where(self, column, *args):
        """Specifies a where expression.

        Arguments:
            column {string} -- The name of the column to search

        Keyword Arguments:
            args {List} -- The operator and the value of the column to search. (default: {None})

        Returns:
            self
        """
        operator, value = self._extract_operator_value(*args)

        if inspect.isfunction(column):
            builder = column(self.new())
            self._wheres += (
                (QueryExpression(None, operator, SubGroupExpression(builder))),
            )
        elif isinstance(column, dict):
            for key, value in column.items():

                self._wheres += ((QueryExpression(key, "=", value, "value")),)
        elif isinstance(value, QueryBuilder):
            self._wheres += (
                (QueryExpression(column, operator, SubSelectExpression(value))),
            )
        else:
            self._wheres += ((QueryExpression(column, operator, value, "value")),)
        return self

    def where_from_builder(self, builder):
        """Specifies a where expression.

        Arguments:
            column {string} -- The name of the column to search

        Keyword Arguments:
            args {List} -- The operator and the value of the column to search. (default: {None})

        Returns:
            self
        """

        self._wheres += ((QueryExpression(None, "=", SubGroupExpression(builder))),)

        return self

    def where_like(self, column, value):
        """Specifies a where expression.

        Arguments:
            column {string} -- The name of the column to search

        Keyword Arguments:
            args {List} -- The operator and the value of the column to search. (default: {None})

        Returns:
            self
        """
        return self.where(column, "like", value)

    def where_not_like(self, column, value):
        """Specifies a where expression.

        Arguments:
            column {string} -- The name of the column to search

        Keyword Arguments:
            args {List} -- The operator and the value of the column to search. (default: {None})

        Returns:
            self
        """
        return self.where(column, "not like", value)

    def where_raw(self, query: str, bindings=()):
        """Specifies raw SQL that should be injected into the where expression.

        Arguments:
            query {string} -- The raw query string.

        Keyword Arguments:
            bindings {tuple} -- query bindings that should be added to the connection. (default: {()})

        Returns:
            self
        """
        self._wheres += (
            (QueryExpression(query, "=", None, "value", raw=True, bindings=bindings)),
        )
        return self

    def or_where(self, column: [str, int], *args) -> "self":
        """Specifies an or where query expression.

        Arguments:
            column {[type]} -- [description]
            value {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        operator, value = self._extract_operator_value(*args)
        if inspect.isfunction(column):
            builder = column(self.new())
            self._wheres += (
                (
                    QueryExpression(
                        None, operator, SubGroupExpression(builder), keyword="or"
                    )
                ),
            )
        elif isinstance(value, QueryBuilder):
            self._wheres += (
                (QueryExpression(column, operator, SubSelectExpression(value))),
            )
        else:
            self._wheres += (
                (QueryExpression(column, operator, value, "value", keyword="or")),
            )
        return self

    def where_exists(self, value: "str|int|QueryBuilder"):
        """Specifies a where exists expression.

        Arguments:
            value {string|int|QueryBuilder} -- A value to check for the existence of a query expression.

        Returns:
            self
        """
        if isinstance(value, QueryBuilder):
            self._wheres += (
                (QueryExpression(None, "EXISTS", SubSelectExpression(value))),
            )
        else:
            self._wheres += ((QueryExpression(None, "EXISTS", value, "value")),)

        return self

    def where_not_exists(self, value: "str|int|QueryBuilder"):
        """Specifies a where exists expression.

        Arguments:
            value {string|int|QueryBuilder} -- A value to check for the existence of a query expression.

        Returns:
            self
        """
        if isinstance(value, QueryBuilder):
            self._wheres += (
                (QueryExpression(None, "NOT EXISTS", SubSelectExpression(value))),
            )
        else:
            self._wheres += ((QueryExpression(None, "NOT EXISTS", value, "value")),)

        return self

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
        self._having += ((HavingExpression(column, equality, value)),)
        return self

    def where_null(self, column):
        """Specifies a where expression where the column is NULL.

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        self._wheres += ((QueryExpression(column, "=", None, "NULL")),)
        return self

    def chunk(self, chunk_amount):
        chunk_connection = self.new_connection()
        for result in chunk_connection.select_many(self.to_sql(), (), chunk_amount):

            yield self.prepare_result(result)

    def where_not_null(self, column: str):
        """Specifies a where expression where the column is not NULL.

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        self._wheres += ((QueryExpression(column, "=", True, "NOT NULL")),)
        return self

    def between(self, column: str, low: [str, int], high: [str, int]):
        """Specifies a where between expression.

        Arguments:
            column {string} -- The name of the column.
            low {string} -- The value on the low end.
            high {string} -- The value on the high end.

        Returns:
            self
        """
        self._wheres += (BetweenExpression(column, low, high),)
        return self

    def where_between(self, *args, **kwargs):
        return self.between(*args, **kwargs)

    def where_not_between(self, *args, **kwargs):
        return self.not_between(*args, **kwargs)

    def not_between(self, column: str, low: [str, int], high: [str, int]):
        """Specifies a where not between expression.

        Arguments:
            column {string} -- The name of the column.
            low {string} -- The value on the low end.
            high {string} -- The value on the high end.

        Returns:
            self
        """
        self._wheres += (BetweenExpression(column, low, high, equality="NOT BETWEEN"),)
        return self

    def where_in(self, column, wheres=None):
        """Specifies where a column contains a list of a values.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            wheres {list} -- A list of values (default: {[]})

        Returns:
            self
        """

        wheres = wheres or []

        if not wheres:
            self._wheres += ((QueryExpression(0, "=", 1, "value_equals")),)

        elif isinstance(wheres, QueryBuilder):
            self._wheres += (
                (QueryExpression(column, "IN", SubSelectExpression(wheres))),
            )
        elif callable(wheres):
            self._wheres += (
                (
                    QueryExpression(
                        column, "IN", SubSelectExpression(wheres(self.new()))
                    )
                ),
            )
        else:
            wheres = [str(x) for x in wheres]
            self._wheres += ((QueryExpression(column, "IN", wheres)),)
        return self

    def get_relation(self, relationship, builder=None):
        if not builder:
            builder = self

        if not builder._model:
            raise AttributeError(
                "You must specify a model in order to use relationship methods"
            )

        return getattr(builder._model, relationship)

    def has(self, *relationships):
        if not self._model:
            raise AttributeError(
                "You must specify a model in order to use 'has' relationship methods"
            )

        for relationship in relationships:
            if "." in relationship:
                last_builder = self._model.builder
                for split_relationship in relationship.split("."):
                    related = last_builder.get_relation(split_relationship)
                    last_builder = related.query_has(last_builder)
            else:
                related = getattr(self._model, relationship)
                related.query_has(self)
        return self

    def where_has(self, relationship, callback):
        getattr(self._model, relationship).get_where_exists_query(self, callback)
        return self

    def with_count(self, relationship, callback=None):
        return getattr(self._model, relationship).get_with_count_query(
            self, callback=callback
        )

    def where_not_in(self, column, wheres=None):
        """Specifies where a column does not contain a list of a values.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            wheres {list} -- A list of values (default: {[]})

        Returns:
            self
        """

        wheres = wheres or []

        if isinstance(wheres, QueryBuilder):
            self._wheres += (
                (QueryExpression(column, "NOT IN", SubSelectExpression(wheres))),
            )
        else:
            wheres = [str(x) for x in wheres]
            self._wheres += ((QueryExpression(column, "NOT IN", wheres)),)
        return self

    def join(
        self, table: str, column1=None, equality=None, column2=None, clause="inner"
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
        if inspect.isfunction(column1):
            self._joins += (column1(JoinClause(table, clause=clause)),)
        elif isinstance(table, str):
            self._joins += (
                JoinClause(table, clause=clause).on(column1, equality, column2),
            )
        else:
            self._joins += (table,)
        return self

    def left_join(self, table, column1=None, equality=None, column2=None):
        """A helper method to add a left join expression.

        Arguments:
            table {string} -- The name of the table to join on.
            column1 {string} -- The name of the foreign table.
            equality {string} -- The equality to join on.
            column2 {string} -- The name of the local column.

        Returns:
            self
        """
        return self.join(
            table=table,
            column1=column1,
            equality=equality,
            column2=column2,
            clause="left",
        )

    def right_join(self, table, column1=None, equality=None, column2=None):
        """A helper method to add a right join expression.

        Arguments:
            table {string} -- The name of the table to join on.
            column1 {string} -- The name of the foreign table.
            equality {string} -- The equality to join on.
            column2 {string} -- The name of the local column.

        Returns:
            self
        """
        return self.join(
            table=table,
            column1=column1,
            equality=equality,
            column2=column2,
            clause="right",
        )

    def joins(self, *relationships, clause="inner"):
        for relationship in relationships:
            relation = getattr(self._model, relationship)
            other_table = relation.builder.get_table_name()
            local_table = self.get_table_name()
            self.join(
                other_table,
                f"{local_table}.{relation.local_key}",
                "=",
                f"{other_table}.{relation.foreign_key}",
                clause=clause,
            )

        return self

    def join_on(self, relationship, callback=None, clause="inner"):
        relation = getattr(self._model, relationship)
        other_table = relation.builder.get_table_name()
        local_table = self.get_table_name()
        self.join(
            other_table,
            f"{local_table}.{relation.local_key}",
            "=",
            f"{other_table}.{relation.foreign_key}",
            clause=clause,
        )

        if callback:
            new_from_builder = self.new_from_builder()
            new_from_builder.table(other_table)
            self.where_from_builder(callback(new_from_builder))

        return self

    def where_column(self, column1, column2):
        """Specifies where two columns equal eachother.

        Arguments:
            column1 {string} -- The name of the column.
            column2 {string} -- The name of the column.

        Returns:
            self
        """
        self._wheres += ((QueryExpression(column1, "=", column2, "column")),)
        return self

    def take(self, *args, **kwargs):
        """Alias for limit method"""
        return self.limit(*args, **kwargs)

    def limit(self, amount):
        """Specifies a limit expression.

        Arguments:
            amount {int} -- The number of rows to limit.

        Returns:
            self
        """
        self._limit = amount
        return self

    def offset(self, amount):
        """Specifies an offset expression.

        Arguments:
            amount {int} -- The number of rows to limit.

        Returns:
            self
        """
        self._offset = amount
        return self

    def skip(self, *args, **kwargs):
        """Alias for limit method"""
        return self.offset(*args, **kwargs)

    def update(self, updates: dict, dry=False, force=False):
        """Specifies columns and values to be updated.

        Arguments:
            updates {dictionary} -- A dictionary of columns and values to update.

        Keyword Arguments:
            dry {bool} -- Whether the query should be executed. (default: {False})

        Returns:
            self
        """
        model = None

        additional = {}

        if self._model:
            model = self._model

        if model and model.is_loaded():
            self.where(model.get_primary_key(), model.get_primary_key_value())
            additional.update({model.get_primary_key(): model.get_primary_key_value()})

            self.observe_events(model, "updating")

        # update only attributes with changes
        if model and not model.__force_update__ and not force:
            changes = {}
            for attribute, value in updates.items():
                if model.__original_attributes__.get(attribute, None) != value:
                    changes.update({attribute: value})
            updates = changes

        # do not perform update query if no changes
        if len(updates.keys()) == 0:
            return model if model else self

        self._updates = (UpdateQueryExpression(updates),)
        self.set_action("update")
        if dry or self.dry:
            return self

        additional.update(updates)

        result = self.new_connection().query(self.to_qmark(), self._bindings)
        if model:
            model.fill(result)
            self.observe_events(model, "updated")
            return model
        return additional

    def force_update(self, updates: dict, dry=False):
        return self.update(updates, dry=dry, force=True)

    def set_updates(self, updates: dict, dry=False):
        """Specifies columns and values to be updated.

        Arguments:
            updates {dictionary} -- A dictionary of columns and values to update.

        Keyword Arguments:
            dry {bool} -- Whether the query should be executed. (default: {False})

        Returns:
            self
        """
        self._updates += (UpdateQueryExpression(updates),)
        return self

    def increment(self, column, value=1):
        """Increments a column's value.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            value {int} -- The value to increment by. (default: {1})

        Returns:
            self
        """
        self._updates += (
            UpdateQueryExpression(column, value, update_type="increment"),
        )
        self.set_action("update")
        return self

    def decrement(self, column, value=1):
        """Decrements a column's value.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            value {int} -- The value to decrement by. (default: {1})

        Returns:
            self
        """
        self._updates += (
            UpdateQueryExpression(column, value, update_type="decrement"),
        )
        self.set_action("update")
        return self

    def sum(self, column):
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        self.aggregate("SUM", "{column}".format(column=column))
        return self

    def count(self, column=None):
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        alias = "m_count_reserved" if (column == "*" or column is None) else column
        if column == "*":
            self.aggregate("COUNT", f"{column} as {alias}")
        elif column is None:
            self.aggregate("COUNT", f"* as {alias}")
        else:
            self.aggregate("COUNT", f"{column}")

        if self.dry:
            return self

        if not column:
            result = self.new_connection().query(
                self.to_qmark(), self._bindings, results=1
            )

            if isinstance(result, dict):
                return result.get(alias, 0)

            prepared_result = list(result.values())
            if not prepared_result:
                return 0
            return prepared_result[0]
        else:
            return self

    def cast_value(self, value):

        if isinstance(value, datetime):
            return str(pendulum.instance(value))
        elif isinstance(value, datetimedate):
            return str(pendulum.datetime(value.year, value.month, value.day))
        elif isinstance(value, datetimetime):
            return str(pendulum.parse(f"{value.hour}:{value.minute}:{value.second}"))

        return value

    def cast_dates(self, result):
        if isinstance(result, dict):
            new_dict = {}
            for key, value in result.items():
                new_dict.update({key: self.cast_value(value)})

            return new_dict
        elif isinstance(result, list):
            new_list = []
            for res in result:
                new_list.append(self.cast_dates(res))
            return new_list

        return result

    def max(self, column):
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        self.aggregate("MAX", "{column}".format(column=column))
        return self

    def order_by(self, column, direction="ASC"):
        """Specifies a column to order by.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            direction {string} -- Specify either ASC or DESC order. (default: {"ASC"})

        Returns:
            self
        """
        for col in column.split(","):
            self._order_by += (OrderByExpression(col, direction=direction),)
        return self

    def order_by_raw(self, query, bindings=()):
        """Specifies a column to order by.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            direction {string} -- Specify either ASC or DESC order. (default: {"ASC"})

        Returns:
            self
        """
        self._order_by += (OrderByExpression(query, raw=True, bindings=bindings),)
        return self

    def group_by(self, column):
        """Specifies a column to group by.

        Arguments:
            column {string} -- The name of the column to group by.

        Returns:
            self
        """
        for col in column.split(","):
            self._group_by += (GroupByExpression(column=col),)

        return self

    def group_by_raw(self, query, bindings=()):
        """Specifies a column to group by.

        Arguments:
            column {string} -- The name of the column to group by.

        Returns:
            self
        """
        self._group_by += (
            GroupByExpression(column=query, raw=True, bindings=bindings),
        )

        return self

    def aggregate(self, aggregate, column, alias=None):
        """Helper function to aggregate.

        Arguments:
            aggregate {string} -- The name of the aggregation.
            column {string} -- The name of the column to aggregate.
        """
        self._aggregates += (
            AggregateExpression(aggregate=aggregate, column=column, alias=alias),
        )

    def first(self, query=False):
        """Gets the first record.

        Returns:
            dictionary -- Returns a dictionary of results.
        """

        if query:
            return self.limit(1)

        result = self.new_connection().query(
            self.limit(1).to_qmark(), self._bindings, results=1
        )

        return self.prepare_result(result)

    def last(self, column=None, query=False):
        """Gets the last record, ordered by column in descendant order or primary
        key if no column is given.

        Returns:
            dictionary -- Returns a dictionary of results.
        """
        _column = column if column else self._model.get_primary_key()
        if query:
            return self.limit(1).order_by(_column, direction="DESC")

        result = self.new_connection().query(
            self.limit(1).order_by(_column, direction="DESC").to_qmark(),
            self._bindings,
            results=1,
        )

        return self.prepare_result(result)

    def _get_eager_load_result(self, related, collection):
        return related.eager_load_from_collection(collection)

    def find(self, record_id):
        """Finds a row by the primary key ID. Requires a model

        Arguments:
            record_id {int} -- The ID of the primary key to fetch.

        Returns:
            Model|None
        """

        return self.where(self._model.get_primary_key(), record_id).first()

    def find_or_fail(self, record_id):
        """Finds a row by the primary key ID (Requires a model) or raise a ModelNotFound exception.

        Arguments:
            record_id {int} -- The ID of the primary key to fetch.

        Returns:
            Model|ModelNotFound
        """

        result = self.find(record_id=record_id)

        if not result:
            raise ModelNotFound()

        return result

    def find_or_404(self, record_id):
        """Finds a row by the primary key ID (Requires a model) or raise an 404 exception.

        Arguments:
            record_id {int} -- The ID of the primary key to fetch.

        Returns:
            Model|HTTP404
        """

        try:
            return self.find_or_fail(record_id)
        except ModelNotFound:
            raise HTTP404()

    def first_or_fail(self, query=False):
        """Returns the first row from database. If no result found a ModelNotFound exception.

        Returns:
            dictionary|ModelNotFound
        """

        if query:
            return self.limit(1)

        result = self.first()

        if not result:
            raise ModelNotFound()

        return result

    def get_primary_key(self):
        return self._model.get_primary_key()

    def prepare_result(self, result, collection=False):
        if self._model and result:
            # eager load here
            hydrated_model = self._model.hydrate(result)
            if self._eager_relation.eagers and hydrated_model:
                for eager_load in self._eager_relation.get_eagers():
                    if isinstance(eager_load, dict):
                        # Nested
                        for relation, eagers in eager_load.items():
                            if inspect.isclass(self._model):
                                related = getattr(self._model, relation)
                            else:
                                related = self._model.get_related(relation)

                            result_set = related.get_related(
                                self, hydrated_model, eagers=eagers
                            )

                            self._register_relationships_to_model(
                                related,
                                result_set,
                                hydrated_model,
                                relation_key=relation,
                            )
                    else:
                        # Not Nested
                        for eager in eager_load:
                            if inspect.isclass(self._model):
                                related = getattr(self._model, eager)
                            else:
                                related = self._model.get_related(eager)

                            result_set = related.get_related(self, hydrated_model)

                            self._register_relationships_to_model(
                                related, result_set, hydrated_model, relation_key=eager
                            )

            if collection:
                return hydrated_model if result else Collection([])
            else:
                return hydrated_model if result else None

        if collection:
            return Collection(result) if result else Collection([])
        else:
            return result or None

    def _register_relationships_to_model(
        self, related, related_result, hydrated_model, relation_key
    ):
        """Takes a related result and a hydrated model and registers them to eachother using the relation key.

        Args:
            related_result (Model|Collection): Will be the related result based on the type of relationship.
            hydrated_model (Model|Collection): If a collection we will need to loop through the collection of models
                                                and register each one individually. Else we can just load the
                                                related_result into the hydrated_models
            relation_key (string): A key to bind the relationship with. Defaults to None.

        Returns:
            self
        """
        if isinstance(hydrated_model, Collection):
            for model in hydrated_model:
                if isinstance(related_result, Collection):
                    related.register_related(relation_key, model, related_result)
                else:
                    model.add_relation({relation_key: related_result or None})
        else:
            hydrated_model.add_relation({relation_key: related_result or None})
        return self

    def all(self, selects=[], query=False):
        """Returns all records from the table.

        Returns:
            dictionary -- Returns a dictionary of results.
        """
        self.select(*selects)
        if query:
            return self.to_sql()

        result = self.new_connection().query(self.to_qmark(), self._bindings) or []

        return self.prepare_result(result, collection=True)

    def get(self, selects=[]):
        """Runs the select query built from the query builder.

        Returns:
            self
        """
        self.select(*selects)
        result = self.new_connection().query(self.to_qmark(), self._bindings)

        return self.prepare_result(result, collection=True)

    def new_connection(self):
        if self._connection:
            return self._connection

        self._connection = self.connection_class(
            **self.get_connection_information(), name=self.connection
        ).make_connection()
        return self._connection

    def get_connection(self):
        return self._connection

    def without_eager(self):
        self._should_eager = False
        return self

    def with_(self, *eagers):
        self._eager_relation.register(eagers)
        return self

    def paginate(self, per_page, page=1):
        if page == 1:
            offset = 0
        else:
            offset = (int(page) * per_page) - per_page

        new_from_builder = self.new_from_builder()
        new_from_builder._order_by = ()
        new_from_builder._columns = ()

        result = self.limit(per_page).offset(offset).get()
        total = new_from_builder.count()

        paginator = LengthAwarePaginator(result, per_page, page, total)
        return paginator

    def simple_paginate(self, per_page, page=1):
        if page == 1:
            offset = 0
        else:
            offset = (int(page) * per_page) - per_page

        result = self.limit(per_page).offset(offset).get()

        paginator = SimplePaginator(result, per_page, page)
        return paginator

    def set_action(self, action):
        """Sets the action that the query builder should take when the query is built.

        Arguments:
            action {string} -- The action that the query builder should take.

        Returns:
            self
        """
        self._action = action
        return self

    def get_grammar(self):
        """Initializes and returns the grammar class.

        Returns:
            masoniteorm.grammar.Grammar -- An ORM grammar class.
        """

        # Either _creates when creating, otherwise use columns
        columns = self._creates or self._columns

        return self.grammar(
            columns=columns,
            table=self._table,
            wheres=self._wheres,
            limit=self._limit,
            offset=self._offset,
            updates=self._updates,
            aggregates=self._aggregates,
            order_by=self._order_by,
            group_by=self._group_by,
            lock=self.lock,
            joins=self._joins,
            having=self._having,
        )

    def to_sql(self):
        """Compiles the QueryBuilder class into a SQL statement.

        Returns:
            self
        """
        for name, scope in self._global_scopes.get(self._action, {}).items():
            scope(self)

        grammar = self.get_grammar()
        sql = grammar.compile(self._action, qmark=False).to_sql()
        return sql

    def run_scopes(self):
        for name, scope in self._global_scopes.get(self._action, {}).items():
            scope(self)

        return self

    def to_qmark(self):
        """Compiles the QueryBuilder class into a Qmark SQL statement.

        Returns:
            self
        """
        grammar = self.get_grammar()

        for name, scope in self._global_scopes.get(self._action, {}).items():
            scope(self)

        grammar = self.get_grammar()
        sql = grammar.compile(self._action, qmark=True).to_sql()

        self._bindings = grammar._bindings

        self.reset()

        return sql

    def new(self):
        """Creates a new QueryBuilder class.

        Returns:
            QueryBuilder -- The ORM QueryBuilder class.
        """
        builder = QueryBuilder(
            grammar=self.grammar,
            connection_class=self.connection_class,
            connection=self.connection,
            connection_driver=self._connection_driver,
        )

        if self._table:
            builder.table(self._table.name)

        return builder

    def avg(self, column):
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        self.aggregate("AVG", "{column}".format(column=column))
        return self

    def min(self, column):
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        self.aggregate("MIN", "{column}".format(column=column))
        return self

    def _extract_operator_value(self, *args):

        operators = ["=", ">", ">=", "<", "<=", "!=", "<>", "like", "not like"]

        operator = operators[0]

        value = None

        if (len(args)) >= 2:
            operator = args[0]
            value = args[1]
        elif len(args) == 1:
            value = args[0]

        if operator not in operators:
            raise ValueError(
                "Invalid comparison operator. The operator can be %s"
                % ", ".join(operators)
            )

        return operator, value

    def __call__(self):
        """Magic method to standardize what happens when the query builder object is called.

        Returns:
            self
        """
        return self

    def macro(self, name, callable):
        self._macros.update({name: callable})
        return self

    def when(self, conditional, callback):
        if conditional:
            callback(self)
        return self

    def truncate(self, foreign_keys=False):
        sql = self.get_grammar().truncate_table(self.get_table_name(), foreign_keys)
        if self.dry:
            return sql

        return self.new_connection().query(sql, ())

    def new_from_builder(self, from_builder=None):
        """Creates a new QueryBuilder class.

        Returns:
            QueryBuilder -- The ORM QueryBuilder class.
        """
        if from_builder is None:
            from_builder = self

        builder = QueryBuilder(
            grammar=self.grammar,
            connection_class=self.connection_class,
            connection=self.connection,
            connection_driver=self._connection_driver,
        )

        if self._table:
            builder.table(self._table.name)

        builder._columns = from_builder._columns
        builder._creates = from_builder._creates
        builder._sql = from_builder._sql = ""
        builder._bindings = from_builder._bindings
        builder._updates = from_builder._updates
        builder._wheres = from_builder._wheres
        builder._order_by = from_builder._order_by
        builder._group_by = from_builder._group_by
        builder._joins = from_builder._joins
        builder._having = from_builder._having
        builder._macros = from_builder._macros
        builder._aggregates = from_builder._aggregates

        return builder
