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


class JoinExpression:
    """A helper class to manage join expressions."""

    def __init__(self, foreign_table, column1, equality, column2, clause="inner"):
        self.foreign_table = foreign_table
        self.column1 = column1
        self.equality = equality
        self.column2 = column2
        self.clause = clause


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

    def __init__(self, builder):
        self.builder = builder


class SelectExpression:
    """A helper class to manage select expressions."""

    def __init__(self, column, raw=False):
        self.column = column
        self.raw = raw
