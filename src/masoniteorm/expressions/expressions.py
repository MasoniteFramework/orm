import inspect

from ..helpers.misc import deprecated


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
            self.table = table.split(" as ")[0]
            self.alias = table.split(" as ")[1]

    def on(self, column1, equality, column2):
        self.on_clauses.append(OnClause(column1, equality, column2))
        return self

    def or_on(self, column1, equality, column2):
        self.on_clauses.append(OnClause(column1, equality, column2, "or"))
        return self

    def on_value(self, column, *args):
        equality, value = self._extract_operator_value(*args)
        self.on_clauses += ((OnValueClause(column, equality, value, "value")),)
        return self

    def or_on_value(self, column, *args):
        equality, value = self._extract_operator_value(*args)
        self.on_clauses += (
            (OnValueClause(column, equality, value, "value", operator="or")),
        )
        return self

    def on_null(self, column):
        """Specifies an ON expression where the column IS NULL.

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        self.on_clauses += ((OnValueClause(column, "=", None, "NULL")),)
        return self

    def on_not_null(self, column: str):
        """Specifies an ON expression where the column IS NOT NULL.

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        self.on_clauses += ((OnValueClause(column, "=", True, "NOT NULL")),)
        return self

    def or_on_null(self, column):
        """Specifies an ON expression where the column IS NULL.

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        self.on_clauses += ((OnValueClause(column, "=", None, "NULL", operator="or")),)
        return self

    def or_on_not_null(self, column: str):
        """Specifies an ON expression where the column IS NOT NULL.

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        self.on_clauses += (
            (OnValueClause(column, "=", True, "NOT NULL", operator="or")),
        )
        return self

    @deprecated("Using where() in a Join clause has been superceded by on_value()")
    def where(self, column, *args):
        return self.on_value(column, *args)

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

    def get_on_clauses(self):
        return self.on_clauses


class OnClause:
    def __init__(self, column1, equality, column2, operator="and"):
        self.column1 = column1
        self.column2 = column2
        self.equality = equality
        self.operator = operator


class OnValueClause:
    """A helper class to manage ON expressions in joins with a value."""

    def __init__(
        self,
        column,
        equality,
        value,
        value_type="value",
        keyword=None,
        raw=False,
        bindings=(),
        operator="and",
    ):
        self.column = column
        self.equality = equality
        self.value = value
        self.value_type = value_type
        self.keyword = keyword
        self.raw = raw
        self.bindings = bindings
        self.operator = operator
