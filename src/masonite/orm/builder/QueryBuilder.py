import inspect

from ..collection.Collection import Collection
from ..connections.ConnectionFactory import ConnectionFactory
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


class QueryBuilder:
    """A builder class to manage the building and creation of query expressions.
    """

    _action = "select"

    def __init__(
        self,
        grammar=None,
        connection=None,
        table="",
        connection_details={},
        scopes={},
        global_scopes={},
        owner=None,
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
        self.owner = owner
        self.connection = connection
        self.connection_details = connection_details
        self._scopes = {}
        self._global_scopes = global_scopes
        if scopes:
            self._scopes.update(scopes)
        self.boot()
        self.set_action("select")

        # Get the connection and grammar class.
        if not self.grammar:
            from ..grammar.GrammarFactory import GrammarFactory
            from ..connections.ConnectionFactory import ConnectionFactory

            connection_dictionary = self.connection_details.get(
                self.connection_details.get("default")
            )
            grammar = connection_dictionary.get(
                "grammar", None
            ) or connection_dictionary.get("driver")
            driver = connection_dictionary.get("driver")
            self.connection = ConnectionFactory().make(driver)
            self.grammar = GrammarFactory().make(grammar)

        if not self.owner:
            from ..models import QueryResult

            self.owner = QueryResult

    def table(self, table):
        """Sets a table on the query builder

        Arguments:
            table {string} -- The name of the table

        Returns:
            self
        """
        self._table = table
        return self

    def set_scope(self, cls, name):
        """Sets a scope based on a class and maps it to a name.

        Arguments:
            cls {masonite.orm.Model} -- An ORM model class.
            name {string} -- The name of the scope to use.

        Returns:
            self
        """
        self._scopes.update({name: cls})

        return self

    def set_global_scope(self, cls, name):
        """Sets the global scopes that should be used before creating the SQL.

        Arguments:
            cls {masonite.orm.Model} -- An ORM model class.
            name {string} -- The name of the global scope.

        Returns:
            self
        """
        self._global_scopes.update({name: cls})

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
            return getattr(self._scopes[attribute], attribute)

        raise AttributeError(
            "'QueryBuilder' object has no attribute '{}'".format(attribute)
        )

    def boot(self):
        """Sets various attributes on the query builder class.
        """
        self._columns = ()
        self._creates = {}

        self._sql = ""
        self._sql_binding = ""
        self._bindings = ()

        self._updates = {}

        self._wheres = ()
        self._order_by = ()
        self._group_by = ()
        self._joins = ()
        self._having = ()

        self._aggregates = ()

        self._limit = False
        self._offset = False
        self.set_action("select")

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

    def create(self, creates):
        """Specifies a dictionary that should be used to create new values.

        Arguments:
            creates {dict} -- A dictionary of columns and values.

        Returns:
            self
        """
        self._creates.update(creates)
        self.set_action("insert")
        return self

    def delete(self, column=None, value=None):
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
        return self

    def where(self, column, value=None):
        """Specifies a where expression.

        Arguments:
            column {string} -- The name of the column to search

        Keyword Arguments:
            value {string|None} -- The value of the column to search. (default: {None})

        Returns:
            self
        """
        if inspect.isfunction(column):
            builder = column(self.new())
            self._wheres += ((QueryExpression(None, "=", SubGroupExpression(builder))),)
        elif isinstance(value, QueryBuilder):
            self._wheres += (
                (QueryExpression(column, "=", SubSelectExpression(value))),
            )
        else:
            self._wheres += ((QueryExpression(column, "=", value, "value")),)
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

    def or_where(self, column: [str, int], value: [str, int, callable]) -> "self":
        """Specifies an or where query expression.

        Arguments:
            column {[type]} -- [description]
            value {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        if isinstance(value, QueryBuilder):
            self._wheres += (
                (QueryExpression(column, "=", SubSelectExpression(value))),
            )
        else:
            self._wheres += (
                (QueryExpression(column, "=", value, "value", keyword="or")),
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
        self.where(column, None)
        return self

    def where_not_null(self, column: str):
        """Specifies a where expression where the column is not NULL.

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        self.where(column, True)
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
        if isinstance(wheres, QueryBuilder):
            self._wheres += (
                (QueryExpression(column, "IN", SubSelectExpression(wheres))),
            )
        else:
            wheres = [str(x) for x in wheres]
            self._wheres += ((QueryExpression(column, "IN", wheres)),)
        return self

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
        self._updates = (UpdateQueryExpression(updates),)
        self.set_action("update")
        if dry:
            return self

        return self.connection().make_connection().query(self.to_sql(), self._bindings)

    def increment(self, column, value=1):
        """Increments a column's value.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            value {int} -- The value to increment by. (default: {1})

        Returns:
            self
        """
        self._updates = (UpdateQueryExpression(column, value, update_type="increment"),)
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
        self._updates = (UpdateQueryExpression(column, value, update_type="decrement"),)
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
        self.set_action("select")
        if query:
            return self.limit(1)

        return self.owner.hydrate(
            self.connection()
            .make_connection()
            .query(self.limit(1).to_qmark(), self._bindings, results=1)
        )

    def all(self):
        """Returns all records from the table.

        Returns:
            dictionary -- Returns a dictionary of results.
        """
        return self.owner.hydrate(
            self.connection().make_connection().query(self.to_qmark(), self._bindings)
        )

    def get(self):
        """Runs the select query built from the query builder.

        Returns:
            self
        """
        self.set_action("select")
        result = (
            self.connection().make_connection().query(self.to_qmark(), self._bindings)
        )
        if self.owner._eager_load:
            for eager in self.owner._eager_load:
                relationship_result = (
                    getattr(self.owner, eager)()
                    .where_in("id", Collection(result).pluck("id"))
                    .get()
                )
                self.owner._relationships[eager] = relationship_result
        return self.owner.new_collection(result).map_into(self.owner, "hydrate")

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
            connection_details=self.connection.connection_details
            if self.connection
            else self.connection_details,
        )

    def to_sql(self):
        """Compiles the QueryBuilder class into a SQL statement.

        Returns:
            self
        """

        if not self._action:
            self.set_action("select")

        for scope in self._global_scopes.get(self.owner, {}).get(self._action, []):
            if not scope:
                continue

            scope(self.owner, self)

        grammar = self.get_grammar()

        sql = getattr(
            grammar, "_compile_{action}".format(action=self._action)
        )().to_sql()
        self.boot()
        return sql

    def to_qmark(self):
        """Compiles the QueryBuilder class into a Qmark SQL statement.

        Returns:
            self
        """

        if not self._action:
            self.set_action("select")

        for scope in self._global_scopes.get(self.owner, {}).get(self._action, []):
            if not scope:
                continue

            scope(self.owner, self)

        grammar = self.get_grammar()

        qmark = getattr(grammar, "_compile_{action}".format(action=self._action))(
            qmark=True
        ).to_qmark()

        self.boot()

        self._bindings = grammar._bindings

        return qmark

    def new(self):
        """Creates a new QueryBuilder class.

        Returns:
            QueryBuilder -- The ORM QueryBuilder class.
        """
        builder = QueryBuilder(
            grammar=self.grammar, connection=self.connection, table=self._table
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

    def __call__(self):
        """Magic method to standardize what happens when the query builder object is called.

        Returns:
            self
        """
        return self
