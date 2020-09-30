import inspect

from ..collection.Collection import Collection
from ..expressions.expressions import (
    SubGroupExpression,
    SubSelectExpression,
    SelectExpression,
    BetweenExpression,
    QueryExpression,
    UpdateQueryExpression,
    JoinExpression,
    HavingExpression,
)

from ..scopes import BaseScope

from ..schema import Schema

from .processors import PostProcessorFactory

from ..connections import ConnectionResolver


class QueryBuilder:
    """A builder class to manage the building and creation of query expressions."""

    def __init__(
        self,
        grammar=None,
        connection=None,
        table=None,
        connection_details={},
        connection_driver=None,
        model=None,
        scopes={},
        dry=False,
    ):
        """QueryBuilder initializer

        Arguments:
            grammar {masonite.orm.grammar.Grammar} -- A grammar class.

        Keyword Arguments:
            connection {masonite.orm.connection.Connection} -- A connection class (default: {None})
            table {str} -- the name of the table (default: {""})
        """
        self.grammar = grammar
        self._table = table
        self.connection = connection
        self._connection = None
        self._connection_details = connection_details
        self._connection_driver = connection_driver
        self._scopes = scopes
        self._eager_loads = ()
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
        self._sql_binding = ""
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
            self._connection_details = ConnectionResolver.get_connection_details()

        if self._connection_details and (
            not self._connection_driver or self._connection_driver == "default"
        ):
            # setup the connection information
            self._connection_driver = self._connection_details.get("default")

    def reset(self):
        """Resets the query builder instance so you can make multiple calls with the same builder instance"""

        self.set_action("select")
        self._wheres = ()

        return self

    def get_connection_information(self):
        return {
            "host": self._connection_details.get(self._connection_driver, {}).get(
                "host"
            ),
            "database": self._connection_details.get(self._connection_driver, {}).get(
                "database"
            ),
            "user": self._connection_details.get(self._connection_driver, {}).get(
                "user"
            ),
            "port": self._connection_details.get(self._connection_driver, {}).get(
                "port"
            ),
            "password": self._connection_details.get(self._connection_driver, {}).get(
                "password"
            ),
            "prefix": self._connection_details.get(self._connection_driver, {}).get(
                "prefix"
            ),
        }

    def table(self, table):
        """Sets a table on the query builder

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        self._table = table
        return self

    def get_table_name(self):
        """Sets a table on the query builder

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        return self._table

    def get_connection(self):
        """Sets a table on the query builder

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        return self.connection

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
        return Schema(connection=self.connection, grammar=self.grammar)

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
            cls {masonite.orm.Model} -- An ORM model class.
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
            cls {masonite.orm.Model} -- An ORM model class.
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
            cls {masonite.orm.Model} -- An ORM model class.
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

    def on(self, driver):
        self._connection_driver = driver
        return self

    def select(self, *args):
        """Specifies columns that should be selected

        Returns:
            self
        """
        for column in args:
            self._columns += (SelectExpression(column),)

        return self

    def select_raw(self, string):
        """Specifies raw SQL that should be injected into the select expression.

        Returns:
            self
        """
        self._columns += (SelectExpression(string, raw=True),)
        return self

    def get_processor(self):
        return PostProcessorFactory().make(self._connection_driver)()

    def create(self, creates={}, query=False, id_key="id", **kwargs):
        """Specifies a dictionary that should be used to create new values.

        Arguments:
            creates {dict} -- A dictionary of columns and values.

        Returns:
            self
        """
        if not creates:
            creates = kwargs

        self.set_action("insert")
        self._creates.update(creates)
        if query:
            return self

        connection = self.new_connection()
        query_result = connection.query(self.to_sql(), self._bindings, results=1)

        if self._model:
            id_key = self._model.get_primary_key()

        processed_results = self.get_processor().process_insert_get_id(
            self, query_result or self._creates, id_key
        )

        if self._model:
            return self._model.hydrate(processed_results)

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
        if column and value:
            if isinstance(value, (list, tuple)):
                self.where_in(column, value)
            else:
                self.where(column, value)

        self.set_action("delete")
        if query:
            return self

        return self.new_connection().query(self.to_sql(), self._bindings)

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

        if value is None:
            value = ""
        elif value is True:
            value = "1"
        elif value is False:
            value = "0"

        if inspect.isfunction(column):
            builder = column(self.new())
            self._wheres += (
                (QueryExpression(None, operator, SubGroupExpression(builder))),
            )
        elif isinstance(value, QueryBuilder):
            self._wheres += (
                (QueryExpression(column, operator, SubSelectExpression(value))),
            )
        else:
            self._wheres += ((QueryExpression(column, operator, value, "value")),)
        return self

    def where_raw(self, query: str, bindings=()):
        """Specifies raw SQL that should be injected into the where expression.

        Arguments:
            query {string} -- The raw query string.

        Keyword Arguments:
            bindings {tuple} -- query bindings that should be added to the connection. (default: {()})

        Returns:
            self
        """
        self._wheres += ((QueryExpression(query, "=", None, "value", raw=True)),)
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

    def where_exists(self, value: [str, int, "QueryBuilder"]):
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

    def where_in(self, column, wheres=[]):
        """Specifies where a column contains a list of a values.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            wheres {list} -- A list of values (default: {[]})

        Returns:
            self
        """
        if not wheres:
            self._wheres += ((QueryExpression(0, "=", 1, "value_equals")),)

        elif isinstance(wheres, QueryBuilder):
            self._wheres += (
                (QueryExpression(column, "IN", SubSelectExpression(wheres))),
            )
        else:
            wheres = [str(x) for x in wheres]
            self._wheres += ((QueryExpression(column, "IN", wheres)),)
        return self

    #         if "." in has_relationship:
    #             # Get nested relationship
    #             last_builder = cls.builder
    #             for split_has_relationship in has_relationship.split("."):
    #                 local_key = cls._registered_relationships[last_builder.owner][
    #                     split_has_relationship
    #                 ]["local"]
    #                 foreign_key = cls._registered_relationships[last_builder.owner][
    #                     split_has_relationship
    #                 ]["foreign"]
    #                 relationship = last_builder.get_relation(split_has_relationship)()

    #                 last_builder.where_exists(
    #                     relationship.where_column(
    #                         f"{relationship.get_table_name()}.{foreign_key}",
    #                         f"{last_builder.get_table_name()}.{local_key}",
    #                     )
    #                 )

    #                 last_builder = relationship

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
                    related_builder = related.get_builder()
                    last_builder.where_exists(
                        related_builder.where_column(
                            f"{related_builder.get_table_name()}.{related.foreign_key}",
                            f"{last_builder.get_table_name()}.{related.local_key}",
                        )
                    )
                    last_builder = related_builder
            else:
                related = getattr(self._model, relationship)
                related_builder = related.get_builder()
                self.where_exists(
                    related_builder.where_column(
                        f"{related_builder.get_table_name()}.{related.foreign_key}",
                        f"{self.get_table_name()}.{related.local_key}",
                    )
                )
        return self

    def where_has(self, relationship, callback):
        related = getattr(self._model, relationship)
        related_builder = related.get_builder()
        self.where_exists(
            related_builder.where_column(
                f"{related_builder.get_table_name()}.{related.foreign_key}",
                f"{self.get_table_name()}.{related.local_key}",
            )
        )

        callback(related_builder)

        return self
        # return self.owner.where_has(*args, **kwargs)

    def where_not_in(self, column, wheres=[]):
        """Specifies where a column does not contain a list of a values.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            wheres {list} -- A list of values (default: {[]})

        Returns:
            self
        """
        if isinstance(wheres, QueryBuilder):
            self._wheres += (
                (QueryExpression(column, "NOT IN", SubSelectExpression(wheres))),
            )
        else:
            wheres = [str(x) for x in wheres]
            self._wheres += ((QueryExpression(column, "NOT IN", wheres)),)
        return self

    def join(
        self,
        foreign_table: str,
        column1: str,
        equality: ["=", "<", "<=", ">", ">="],
        column2: str,
        clause="inner",
    ):
        """Specifies a join expression.

        Arguments:
            foreign_table {string} -- The name of the table to join on.
            column1 {string} -- The name of the foreign table.
            equality {string} -- The equality to join on.
            column2 {string} -- The name of the local column.

        Keyword Arguments:
            clause {string} -- The action clause. (default: {"inner"})

        Returns:
            self
        """
        self._joins += (
            JoinExpression(foreign_table, column1, equality, column2, clause=clause),
        )
        return self

    def left_join(self, foreign_table, column1, equality, column2):
        """A helper method to add a left join expression.

        Arguments:
            foreign_table {string} -- The name of the table to join on.
            column1 {string} -- The name of the foreign table.
            equality {string} -- The equality to join on.
            column2 {string} -- The name of the local column.

        Returns:
            self
        """
        self._joins += (
            JoinExpression(foreign_table, column1, equality, column2, "left"),
        )
        return self

    def right_join(self, foreign_table, column1, equality, column2):
        """A helper method to add a right join expression.

        Arguments:
            foreign_table {string} -- The name of the table to join on.
            column1 {string} -- The name of the foreign table.
            equality {string} -- The equality to join on.
            column2 {string} -- The name of the local column.

        Returns:
            self
        """
        self._joins += (
            JoinExpression(foreign_table, column1, equality, column2, "right"),
        )
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

    def update(self, updates: dict, dry=False):
        """Specifies columns and values to be updated.

        Arguments:
            updates {dictionary} -- A dictionary of columns and values to update.

        Keyword Arguments:
            dry {bool} -- Whether the query should be executed. (default: {False})

        Returns:
            self
        """
        self._updates += (UpdateQueryExpression(updates),)
        self.set_action("update")
        if dry:
            return self

        return self.new_connection().query(self.to_sql(), self._bindings)

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

    def count(self, column="*"):
        """Aggregates a columns values.

        Arguments:
            column {string} -- The name of the column to aggregate.

        Returns:
            self
        """
        self.aggregate("COUNT", "{column}".format(column=column))
        return self

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
        self._order_by += ((column, direction),)
        return self

    def group_by(self, column):
        """Specifies a column to group by.

        Arguments:
            column {string} -- The name of the column to group by.

        Returns:
            self
        """
        self._group_by += (column,)
        return self

    def aggregate(self, aggregate, column):
        """Helper function to aggregate.

        Arguments:
            aggregate {string} -- The name of the aggregation.
            column {string} -- The name of the column to aggregate.
        """
        self._aggregates += ((aggregate, column),)

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

    def _get_eager_load_result(self, related, collection):
        return related.eager_load_from_collection(collection)

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
                    model.add_relation({relation_key: related_result})
        else:
            hydrated_model.add_relation({relation_key: related_result})
        return self

    def get_primary_key(self):
        return self._model.get_primary_key()

    def prepare_result(self, result, collection=False):
        if self._model:
            # eager load here
            hydrated_model = self._model.hydrate(result)
            if self._eager_loads and hydrated_model:
                for eager in set(self._eager_loads):
                    related = getattr(self._model, eager)
                    related_result = related.get_related(hydrated_model)
                    self._register_relationships_to_model(
                        related, related_result, hydrated_model, relation_key=eager
                    )

            if collection:
                return hydrated_model if result else Collection([])
            else:
                return hydrated_model if result else None

        if collection:
            return result or Collection([])
        else:
            return result or None

    def all(self, query=False):
        """Returns all records from the table.

        Returns:
            dictionary -- Returns a dictionary of results.
        """
        if query:
            return self.to_sql()

        result = self.new_connection().query(self.to_qmark(), self._bindings) or []

        return self.prepare_result(result, collection=True)

    def get(self):
        """Runs the select query built from the query builder.

        Returns:
            self
        """
        result = self.new_connection().query(self.to_qmark(), self._bindings)

        return self.prepare_result(result, collection=True)

    def new_connection(self):
        if self._connection:
            return self._connection

        self._connection = self.connection(
            **self.get_connection_information()
        ).make_connection()
        return self._connection

    def get_connection(self):
        return self._connection

    def without_eager(self):
        self._should_eager = False
        return self

    def with_(self, eagers=()):
        if not isinstance(eagers, (tuple, list)):
            eagers = (eagers,)

        self._eager_loads += tuple(eagers)
        return self

    # def eager_load_model(self, result):
    #     eager_dic = {}
    #     if not self._should_eager:
    #         return {}

    #     for eager in self._eager_loads:
    #         if "." in eager:
    #             last_owner = self.owner
    #             last_eager = None
    #             for split_eager in eager.split("."):
    #                 if split_eager in eager_dic:
    #                     related = getattr(last_owner, split_eager)()
    #                     last_owner = related.owner
    #                     last_eager = split_eager
    #                     continue

    #                 relationship = last_owner._registered_relationships[last_owner][
    #                     split_eager
    #                 ]
    #                 foreign_key, local_key = (
    #                     relationship["foreign"],
    #                     relationship["local"],
    #                 )
    #                 related = getattr(last_owner, split_eager)()

    #                 result = (
    #                     related.without_eager()
    #                     .where_in(
    #                         foreign_key,
    #                         Collection(result).unique(local_key).pluck(local_key),
    #                     )
    #                     .get()
    #                 )

    #                 # try to load the inners into the outer query
    #                 # For logo need to get articles and loop through collection
    #                 if last_eager and last_eager in eager_dic:
    #                     eager_dic[last_eager].add_relation({split_eager: result})
    #                 else:
    #                     eager_dic.update({split_eager: result})
    #                 last_owner = related.owner
    #                 last_eager = split_eager
    #         else:
    #             relationship = self.owner._registered_relationships[self.owner][eager]

    #             foreign_key, local_key = (
    #                 relationship["foreign"],
    #                 relationship["local"],
    #             )

    #             result = (
    #                 getattr(self.owner, eager)()
    #                 .without_eager()
    #                 .where_in(
    #                     foreign_key,
    #                     Collection(result).unique(local_key).pluck(local_key),
    #                 )
    #                 .get()
    #             )

    #             eager_dic.update({eager: result})

    #     return eager_dic

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
            masonite.orm.grammar.Grammar -- An ORM grammar class.
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
            joins=self._joins,
            having=self._having,
            # connection=self.connection
        )

    def to_sql(self):
        """Compiles the QueryBuilder class into a SQL statement.

        Returns:
            self
        """
        for name, scope in self._global_scopes.get(self._action, {}).items():
            scope(self)

        grammar = self.get_grammar()
        sql = grammar.compile(self._action).to_sql()
        self.reset()
        return sql

    def to_qmark(self):
        """Compiles the QueryBuilder class into a Qmark SQL statement.

        Returns:
            self
        """

        grammar = self.get_grammar()

        for name, scope in self._global_scopes.get(self._action, {}).items():
            scope(self)

        qmark = getattr(grammar, "_compile_{action}".format(action=self._action))(
            qmark=True
        ).to_qmark()

        self.reset()

        self._bindings = grammar._bindings

        return qmark

    def new(self):
        """Creates a new QueryBuilder class.

        Returns:
            QueryBuilder -- The ORM QueryBuilder class.
        """
        builder = QueryBuilder(
            grammar=self.grammar,
            connection=self.connection.__class__,
            connection_driver=self._connection_driver,
            table=self._table,
        )

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

        operators = ["=", ">", ">=", "<", "<=", "!=", "<>"]

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
