import pymysql.cursors
from masonite.testing import TestCase


class MySQLGrammer:

    """The keys in this dictionary is how the ORM will reference these aggregates

    The values on the right are the matching functions for the grammer
    
    Returns:
        [type] -- [description]
    """

    aggregate_options = {
        "SUM": "SUM",
        "MAX": "MAX",
        "MIN": "MIN",
        "AVG": "AVG",
        "COUNT": "COUNT",
        "AVG": "AVG",
    }

    _columns = "*"

    _sql = ""

    _updates = {}

    _aggregates = {}

    table = "users"

    _wheres = ()

    _order_by = ()

    _limit = False

    def __init__(
        self,
        columns="*",
        table="users",
        wheres=(),
        limit=False,
        updates={},
        aggregates=(),
        order_by=(),
    ):
        self._columns = columns
        self.table = table
        self._wheres = wheres
        self._limit = limit
        self._updates = updates
        self._aggregates = aggregates
        self._order_by = order_by

    def _compile_select(self):
        self._sql = (
            self.select_format()
            .format(
                columns=self._compile_columns(seperator=", "),
                table=self._compile_from(),
                wheres=self._compile_wheres(),
                limit=self._compile_limit(),
                aggregates=self._compile_aggregates(),
                order_by=self._compile_order_by(),
            )
            .strip()
        )

        return self

    def _compile_update(self):
        self._sql = "UPDATE {table} SET {key_equals} {wheres}".format(
            key_equals=self._compile_key_value_equals(),
            table=self._compile_from(),
            wheres=self._compile_wheres(),
        )

        return self

    def _compile_insert(self):
        self._sql = "INSERT INTO {table} ({columns}) VALUES ({values})".format(
            key_equals=self._compile_key_value_equals(),
            table=self._compile_from(),
            columns=self._compile_columns(seperator=", "),
            values=self._compile_values(seperator=", "),
        )

        return self

    def _compile_delete(self):
        self._sql = "DELETE FROM {table} {wheres}".format(
            key_equals=self._compile_key_value_equals(),
            table=self._compile_from(),
            wheres=self._compile_wheres(),
        )

        return self

    def _compile_key_value_equals(self):
        sql = ""
        for column, value in self._updates.items():
            sql += self.key_value_string().format(
                column=self._compile_column(column), value=value
            )

        return sql

    def _compile_aggregates(self):
        sql = ""
        for aggregates in self._aggregates:
            aggregate, column = aggregates
            aggregate_function = self.aggregate_options.get(aggregate, "")
            sql += " {aggregate_function}({column}) AS {alias}".format(
                aggregate_function=aggregate_function,
                column=self._compile_column(column),
                alias=self._compile_alias(column),
            )

        return sql

    def _compile_order_by(self):
        print("compiling order by", self._order_by)
        sql = ""
        for order_bys in self._order_by:
            column, direction = order_bys
            sql += "ORDER BY {column} {direction}".format(
                column=self._compile_column(column), direction=direction.upper(),
            )

        return sql

    def select_format(self):
        return "SELECT {columns} FROM {table} {wheres} {order_by} {limit}"

    def key_value_string(self):
        return "{column} = '{value}'"

    def table_string(self):
        return "`{table}`"

    def column_string(self):
        return "`{column}`{seperator}"

    def value_string(self):
        return "'{value}'{seperator}"

    def _compile_alias(self, column):
        return column

    def limit_string(self):
        return "LIMIT {limit}"

    def first_where_string(self):
        return "WHERE"

    def additional_where_string(self):
        return "AND"

    def _compile_from(self):
        return self.table_string().format(table=self.table)

    def _compile_limit(self):
        if not self._limit:
            return ""

        return self.limit_string().format(limit=self._limit)

    def _compile_wheres(self):
        sql = ""
        loop_count = 0
        for where in self._wheres:
            if loop_count == 0:
                keyword = self.first_where_string()
            else:
                keyword = self.additional_where_string()

            column, equality, value = where
            column = self._compile_column(column)
            sql += " {keyword} {column} {equality} '{value}'".format(
                keyword=keyword, column=column, equality=equality, value=value
            )
            loop_count += 1
        return sql

    def select(self, *args):
        self._columns = list(args)
        return self

    def create(self, creates):
        self._columns = creates
        return self

    def delete(self, column, value):
        self.where(column, value)
        return self

    def where(self, column, value):
        self._wheres += ((column, "=", value),)
        return self

    def limit(self, amount):
        self._limit = amount
        return self

    def update(self, updates):
        self._updates = updates
        return self

    def to_sql(self):
        """Cleans up the SQL string and returns the SQL
        
        Returns:
            string
        """
        self._sql = self._sql.strip().replace("  ", " ")
        return self._sql

    def _compile_columns(self, seperator=""):
        sql = ""
        print("compiling columns")

        if self._columns is not "*":
            for column in self._columns:
                sql += self._compile_column(column, seperator=seperator)

        print("compiled columns", sql)

        if self._aggregates:
            sql += self._compile_aggregates()

        print("compiled aggregates", sql)

        if sql == "":
            return "*"

        return sql.rstrip(",").rstrip(", ")

    def _compile_values(self, seperator=""):
        sql = ""
        if self._columns == "*":
            return self._columns

        for column, value in self._columns.items():
            sql += self._compile_value(value, seperator=seperator)

        return sql[:-2]

    def _compile_column(self, column, seperator=""):
        return self.column_string().format(column=column, seperator=seperator)

    def _compile_value(self, value, seperator=""):
        return self.value_string().format(value=value, seperator=seperator)
