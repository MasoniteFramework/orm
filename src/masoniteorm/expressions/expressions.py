class QueryExpression:
    """A helper class to manage query expressions."""

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
    """A helper class to manage having expressions."""

    def __init__(self, column, equality=None, value=None):
        self.column = column

        if equality and not value:
            value = equality
            equality = "="

        self.equality = equality
        self.value = value
        self.value_type = "having"


class FromTable:
    """A helper class to manage having expressions."""

    def __init__(self, name, raw=False):
        self.name = name
        self.raw = raw


class UpdateQueryExpression:
    """A helper class to manage update expressions."""

    def __init__(self, column, value=None, update_type="keyvalue"):
        self.column = column
        self.value = value
        self.update_type = update_type


class BetweenExpression:
    """A helper class to manage where between expressions."""

    def __init__(self, column, low, high, equality="BETWEEN"):
        self.column = column
        self.low = low
        self.high = high
        self.equality = equality
        self.value = None
        self.value_type = "BETWEEN"
        self.raw = False


class SubSelectExpression:
    """A helper class to manage subselect expressions."""

    def __init__(self, builder):
        self.builder = builder


class SubGroupExpression:
    """A helper class to manage subgroup expressions."""

    def __init__(self, builder, alias="group"):
        self.builder = builder
        self.alias = alias


class SelectExpression:
    """A helper class to manage select expressions."""

    def __init__(self, column, raw=False):
        self.column = column.strip()
        self.alias = None
        self.raw = raw
        if raw is False and " as " in self.column:
            self.column, self.alias = self.column.split(" as ")
            self.column = self.column.strip()
            self.alias = self.alias.strip()


class OrderByExpression:
    """A helper class to manage select expressions."""

    def __init__(self, column, direction="ASC", raw=False, bindings=()):
        self.column = column.strip()

        self.raw = raw

        self.direction = direction
        self.bindings = bindings

        if raw is False:
            if self.column.endswith(" desc"):
                self.column = self.column.split(" desc")[0].strip()
                self.direction = "DESC"

            if self.column.endswith(" asc"):
                self.column = self.column.split(" asc")[0].strip()
                self.direction = "ASC"


class GroupByExpression:
    """A helper class to manage select expressions."""

    def __init__(self, column=None, raw=False, bindings=()):
        self.column = column.strip()

        self.raw = raw
        self.bindings = bindings


class AggregateExpression:
    def __init__(self, aggregate=None, column=None, alias=False):
        self.aggregate = aggregate
        self.column = column.strip()
        self.alias = alias
        if " as " in self.column:
            self.column, self.alias = self.column.split(" as ")


class Raw:
    def __init__(self, expression):
        self.expression = expression

class JoinClause:

    def __init__(self, table, clause="join"):
        self.table = table
        self.alias = None
        self.clause = clause
        self.on_clauses = []

        if " as " in self.table:
            self.table = table.split(' as ')[0]
            self.alias = table.split(' as ')[1]

    def on(self, column1, equality, column2):
        self.on_clauses.append(OnClause(column1, equality, column2))
        return self
    
    def get_on_clauses(self):
        return self.on_clauses

class OnClause:

    def __init__(self, column1, equality, column2):
        self.column1 = column1
        self.column2 = column2
        self.equality = equality