import pymysql.cursors
from masonite.testing import TestCase


class BaseGrammar:

    """The keys in this dictionary is how the ORM will reference these aggregates

    The values on the right are the matching functions for the grammar

    Returns:
        [type] -- [description]
    """

    table = "users"

    def __init__(
        self,
        columns="*",
        table="users",
        wheres=(),
        limit=False,
        updates={},
        aggregates=(),
        order_by=(),
        group_by=(),
        creates=(),
        connection_details={},
    ):
        self._columns = columns
        self.table = table
        self._wheres = wheres
        self._limit = limit
        self._updates = updates
        self._aggregates = aggregates
        self._order_by = order_by
        self._group_by = group_by
        self._creates = creates
        self._connection_details = connection_details
        self._column = None

        self._bindings = ()

        self._sql = ""

        self._sql_qmark = ""

    def _compile_create(self):
        sql = self.create_start().format(table=self._compile_from())

        sql += "("
        """Add Columns
        """
        for column in self._creates:
            sql += self.create_column_string().format(
                column=self._compile_column(column.column_name),
                data_type=self.type_map.get(column.column_type),
                length=self.create_column_length().format(length=column.length)
                if column.length
                else "",
                nullable="" if column.is_null else " NOT NULL",
            )

        """Add Constraints
        """
        for column in self._creates:
            if column.is_constraint:
                sql += getattr(
                    self, "{}_constraint_string".format(column.constraint_type)
                )().format(
                    column=self._compile_column(column.column_name),
                    clean_column=column.column_name,
                )
                sql += ", "
        print(sql)
        sql = sql.rstrip(", ")

        sql += ")"

        self._sql = sql
        return self

    def _compile_alter(self):
        sql = self.alter_start().format(table=self._compile_from())

        """Add Columns
        """

        for column in self._creates:
            sql += self.alter_column_string().format(
                column=self._compile_column(column.column_name),
                old_column=self._compile_column(column.old_column),
                data_type=self.type_map.get(column.column_type),
                length=self.create_column_length().format(length=column.length)
                if column.length
                else "",
                nullable="" if column.is_null else " NOT NULL",
                after=self.after_column_string().format(
                    after=self._compile_column(column.after_column)
                )
                if column.after_column
                else "",
            )

        # Fix any inconsistencies
        sql = sql.rstrip(", ").replace(" ,", ",")

        self._sql = sql
        return self

    def _compile_select(self, qmark=False):
        self._sql = (
            self.select_format()
            .format(
                columns=self._compile_columns(seperator=", "),
                table=self._compile_from(),
                wheres=self._compile_wheres(qmark=qmark),
                limit=self._compile_limit(),
                aggregates=self._compile_aggregates(),
                order_by=self._compile_order_by(),
                group_by=self._compile_group_by(),
            )
            .strip()
        )

        return self

    def _compile_update(self, qmark=False):
        self._sql = self.update_format().format(
            key_equals=self._compile_key_value_equals(qmark=qmark),
            table=self._compile_from(),
            wheres=self._compile_wheres(qmark=qmark),
        )

        return self

    def _compile_insert(self):
        self._sql = self.insert_format().format(
            key_equals=self._compile_key_value_equals(),
            table=self._compile_from(),
            columns=self._compile_columns(seperator=", "),
            values=self._compile_values(seperator=", "),
        )

        return self

    def _compile_delete(self):
        self._sql = self.delete_format().format(
            key_equals=self._compile_key_value_equals(),
            table=self._compile_from(),
            wheres=self._compile_wheres(),
        )

        return self

    def _compile_key_value_equals(self, qmark=False):
        sql = ""
        for column, value in self._updates.items():
            print("looping through", column)
            print("getting", self._compile_column(column))
            sql += self.key_value_string().format(
                column=self._compile_column(column), value=value if not qmark else "?"
            )

            print("compiling key value pairs", sql)

            if qmark:
                self._bindings += (value,)

        return sql

    def _compile_aggregates(self):
        sql = ""
        for aggregates in self._aggregates:
            aggregate, column = aggregates
            aggregate_function = self.aggregate_options.get(aggregate, "")
            sql += self.aggregate_string().format(
                aggregate_function=aggregate_function,
                column=self._compile_column(column),
                alias=self._compile_alias(column),
            )

        return sql

    def _compile_order_by(self):
        sql = ""
        for order_bys in self._order_by:
            column, direction = order_bys
            sql += self.order_by_string().format(
                column=self._compile_column(column), direction=direction.upper(),
            )

        return sql

    def _compile_group_by(self):
        sql = ""
        for group_bys in self._group_by:
            column = group_bys
            sql += "GROUP BY {column}".format(column=self._compile_column(column))

        return sql

    def _compile_alias(self, column):
        return column

    def _compile_from(self):
        return self.table_string().format(
            table=self.table,
            database=self._connection_details.get("database", ""),
            prefix=self._connection_details.get("prefix", ""),
        )

    def _compile_limit(self):
        if not self._limit:
            return ""

        return self.limit_string().format(limit=self._limit)

    def _compile_wheres(self, qmark=False):
        sql = ""
        loop_count = 0
        for where in self._wheres:
            print(where)
            column, equality, value = where

            print(column, equality, value)
            if loop_count == 0:
                keyword = self.first_where_string()
            else:
                keyword = self.additional_where_string()

            # if amount:
            #     keyword = self.where_in_string().format(
            #         values=','.join(value) if isinstance(value, list) else ''
            #     )

            column = self._compile_column(column)
            sql += " {keyword} {column} {equality} {value}".format(
                keyword=keyword,
                column=column,
                equality=equality,
                value=("(" + ",".join(value) + ")")
                if isinstance(value, list)
                else self.value_string().format(value=value, seperator="")
                if not qmark
                else "'?'",
            )
            if qmark:
                self._bindings += (value,)
            loop_count += 1

        return sql

    def select(self, *args):
        self._columns = list(args)
        return self

    def create(self, creates):
        self._columns = creates
        return self

    def delete(self, column=None, value=None):
        if column and value:
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

    def column_exists(self, column):
        self._column = column
        self._sql = self._compile_exists()
        return self

    def _compile_exists(self):
        return self.column_exists_string().format(
            table=self._compile_from(), value=self._compile_value(self._column)
        )

    def to_sql(self):
        """Cleans up the SQL string and returns the SQL

        Returns:
            string
        """
        self._sql = self._sql.strip().replace("  ", " ").replace("   ", " ")
        return self._sql

    def to_qmark(self):
        """Cleans up the SQL string and returns the SQL

        Returns:
            string
        """
        self._sql = self._sql.strip().replace("  ", " ").replace("   ", " ")
        return self._sql

    def _compile_columns(self, seperator=""):
        sql = ""

        if self._columns != "*":
            for column in self._columns:
                sql += self._compile_column(column, seperator=seperator)

        if self._aggregates:
            sql += self._compile_aggregates()

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
