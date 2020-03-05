import copy
import inspect
from ..collection.Collection import Collection


class QueryExpression:
    def __init__(
        self,
        column,
        equality,
        value,
        value_type="value",
        keyword=None,
        raw=False,
        bindings=(),
    ):
        self.column = column
        self.equality = equality
        self.value = value
        self.value_type = value_type
        self.keyword = keyword
        self.raw = raw
        self.bindings = bindings


class HavingExpression:
    def __init__(self, column, equality=None, value=None):
        self.column = column

        if equality and not value:
            value = equality
            equality = "="

        self.equality = equality
        self.value = value
        self.value_type = "having"


class JoinExpression:
    def __init__(self, foreign_table, column1, equality, column2, clause="inner"):
        self.foreign_table = foreign_table
        self.column1 = column1
        self.equality = equality
        self.column2 = column2
        self.clause = clause


class UpdateQueryExpression:
    def __init__(self, column, value=None, update_type="keyvalue"):
        self.column = column
        self.value = value
        self.update_type = update_type


class BetweenExpression:
    def __init__(self, column, low, high):
        self.column = column
        self.low = low
        self.high = high
        self.equality = "BETWEEN"
        self.value = None
        self.value_type = "BETWEEN"
        self.raw = False


class SubSelectExpression:
    def __init__(self, builder):
        self.builder = builder


class SubGroupExpression:
    def __init__(self, builder):
        self.builder = builder


class SelectExpression:
    def __init__(self, column, raw=False):
        self.column = column
        self.raw = raw


class QueryBuilder:

    _action = "select"

    def __init__(
        self,
        grammar,
        connection=None,
        table="",
        connection_details={},
        scopes={},
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
        self.table = table
        self.owner = owner
        self.connection = connection
        self.connection_details = connection_details
        self._scopes = {}
        self._global_scopes = {}
        if scopes:
            self._scopes.update(scopes)
        self.boot()
        self.set_action("select")

    def set_scope(self, cls, name):
        self._scopes.update({name: cls})

        return self

    def set_global_scope(self, cls, name):
        self._scopes.update({name: cls})

        return self

    def __getattr__(self, attribute):
        if attribute in self._scopes:
            # print('calling', attribute, 'on', cls)
            return getattr(self._scopes[attribute], attribute)
            # return cls

        raise AttributeError(
            "'QueryBuilder' object has no attribute '{}'".format(attribute)
        )

    def boot(self):
        self._columns = ()

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
        self._action = None

    def select(self, *args):
        for column in args:
            self._columns += (SelectExpression(column),)
        return self

    def select_raw(self, string):
        self._columns += (SelectExpression(string, raw=True),)
        return self

    def create(self, creates):
        self._columns = creates
        self._action = "insert"
        return self

    def delete(self, column=None, value=None):
        if column and value:
            self.where(column, value)
        self._action = "delete"
        return self

    def where(self, column, value=None):
        if inspect.isfunction(column):
            builder = column(self.new())
            self._wheres += ((QueryExpression(None, "=", SubGroupExpression(builder))),)
        elif isinstance(value, QueryBuilder):
            self._wheres += (
                (QueryExpression(column, "=", SubSelectExpression(value))),
            )
        else:
            self._wheres += ((QueryExpression(column, "=", value, "value")),)
        # self._wheres += ((column, "=", value),)
        return self

    def where_raw(self, column, bindings=()):
        self._wheres += ((QueryExpression(column, "=", None, "value", raw=True)),)
        return self

    def or_where(self, column, value):
        if isinstance(value, QueryBuilder):
            self._wheres += (
                (QueryExpression(column, "=", SubSelectExpression(value))),
            )
        else:
            self._wheres += (
                (QueryExpression(column, "=", value, "value", keyword="or")),
            )
        # self._wheres += ((column, "=", value),)
        return self

    def where_exists(self, value):
        if isinstance(value, QueryBuilder):
            self._wheres += (
                (QueryExpression(None, "EXISTS", SubSelectExpression(value))),
            )
        else:
            self._wheres += ((QueryExpression(None, "EXISTS", value, "value")),)
        # self._wheres += ((column, "=", value),)
        return self

    def having(self, column, equality="", value=""):
        self._having += ((HavingExpression(column, equality, value)),)
        return self

    def where_null(self, column):
        self.where(column, None)
        return self

    def where_not_null(self, column):
        self.where(column, True)
        return self

    def between(self, column, low, high):
        self._wheres += (BetweenExpression(column, low, high),)
        return self

    def where_in(self, column, wheres=[]):
        if isinstance(wheres, QueryBuilder):
            self._wheres += (
                (QueryExpression(column, "IN", SubSelectExpression(wheres))),
            )
        else:
            wheres = [str(x) for x in wheres]
            self._wheres += ((QueryExpression(column, "IN", wheres)),)
        return self

    def join(self, foreign_table, column1, equality, column2, clause="inner"):
        self._joins += (
            JoinExpression(foreign_table, column1, equality, column2, clause=clause),
        )
        return self

    def left_join(self, foreign_table, column1, equality, column2):
        self._joins += (
            JoinExpression(foreign_table, column1, equality, column2, "left"),
        )
        return self

    def right_join(self, foreign_table, column1, equality, column2):
        self._joins += (
            JoinExpression(foreign_table, column1, equality, column2, "right"),
        )
        return self

    def where_column(self, column1, column2):
        self._wheres += ((QueryExpression(column1, "=", column2, "column")),)
        return self

    def limit(self, amount):
        self._limit = amount
        return self

    def offset(self, amount):
        self._offset = amount
        return self

    def update(self, updates):
        self._updates = (UpdateQueryExpression(updates),)
        self._action = "update"
        return self

    def increment(self, column, value=1):
        self._updates = (UpdateQueryExpression(column, value, update_type="increment"),)
        self._action = "update"
        return self

    def decrement(self, column, value=1):
        self._updates = (UpdateQueryExpression(column, value, update_type="decrement"),)
        self._action = "update"
        return self

    def sum(self, column):
        self.aggregate("SUM", "{column}".format(column=column))
        return self

    def count(self, column="*"):
        self.aggregate("COUNT", "{column}".format(column=column))
        return self

    def max(self, column):
        self.aggregate("MAX", "{column}".format(column=column))
        return self

    def order_by(self, column, direction="ASC"):
        self._order_by += ((column, direction),)
        return self

    def group_by(self, column):
        self._group_by += (column,)
        return self

    def aggregate(self, aggregate, column):
        self._aggregates += ((aggregate, column),)

    def first(self):
        self._action = "select"
        return (
            self.connection()
            .make_connection()
            .query(self.limit(1).to_qmark(), self._bindings, results=1)
        )

    def all(self):
        return (
            self.connection().make_connection().query(self.to_qmark(), self._bindings)
        )

    def get(self):
        self._action = "select"
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
        self._action = action
        return self

    def get_grammar(self):
        return self.grammar(
            columns=self._columns,
            table=self.table,
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
        grammar = self.get_grammar()

        if not self._action:
            self.set_action("select")

        sql = getattr(
            grammar, "_compile_{action}".format(action=self._action)
        )().to_sql()
        self.boot()
        return sql

    def to_qmark(self):
        grammar = self.grammar(
            columns=self._columns,
            table=self.table,
            wheres=self._wheres,
            limit=self._limit,
            offset=self._offset,
            updates=self._updates,
            aggregates=self._aggregates,
            order_by=self._order_by,
            group_by=self._group_by,
            connection_details=self.connection.connection_details
            if self.connection
            else self.connection_details,
        )

        grammar = getattr(grammar, "_compile_{action}".format(action=self._action))(
            qmark=True
        )
        self.boot()
        self._bindings = grammar._bindings
        return grammar.to_qmark()

    def new(self):
        builder = QueryBuilder(
            grammar=self.grammar, connection=self.connection, table=self.table
        )

        return builder

    def __call__(self):
        return self
