import re

from masonite.testing import TestCase

from src.masonite.orm.builder.QueryBuilder import (
    SubGroupExpression,
    SubSelectExpression,
    SelectExpression,
    BetweenExpression,
)


class BaseGrammar:

    """The keys in this dictionary is how the ORM will reference these aggregates

    The values on the right are the matching functions for the grammar

    Returns:
        [type] -- [description]
    """

    table = "users"

    def __init__(
        self,
        columns=(),
        table="users",
        wheres=(),
        limit=False,
        offset=False,
        updates={},
        aggregates=(),
        order_by=(),
        group_by=(),
        joins=(),
        having=(),
        creates=(),
        connection_details={},
    ):
        self._columns = columns
        self.table = table
        self._wheres = wheres
        self._limit = limit
        self._offset = offset
        self._updates = updates
        self._aggregates = aggregates
        self._order_by = order_by
        self._group_by = group_by
        self._joins = joins
        self._having = having
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

            length_string = (
                self.create_column_length().format(length=column.length)
                if column.length
                else ""
            )
            mapped_time_value = self.timestamp_mapping.get(column.default)

            default_value = mapped_time_value or column.default

            attributes = {
                "column": self._compile_column(column.column_name),
                "data_type": self.type_map.get(column.column_type),
                "length": length_string,
            }

            if default_value:
                attributes.update({"default_value": default_value})
                sql += self.create_column_string_with_default().format(**attributes)
            else:
                attributes.update({"nullable": "" if column.is_null else " NOT NULL"})
                sql += self.create_column_string().format(**attributes)

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
        sql = sql.rstrip(", ")

        sql += ")"

        self._sql = sql
        return self

    def _compile_alter(self):
        sql = self.alter_start().format(table=self._compile_from())

        """Add Columns
        """
        for column in self._creates:
            nullable = ""
            if column.is_null and column._action == "modify":
                nullable = " NULL"
            elif not column.is_null:
                nullable = " NOT NULL"

            sql += getattr(self, "{}_column_string".format(column._action))().format(
                column=self._compile_column(column.column_name),
                old_column=self._compile_column(column.old_column),
                data_type=self.type_map.get(column.column_type),
                length=self.create_column_length().format(length=column.length)
                if column.length
                else "",
                nullable=nullable,
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
                offset=self._compile_offset(),
                aggregates=self._compile_aggregates(),
                order_by=self._compile_order_by(),
                group_by=self._compile_group_by(),
                joins=self._compile_joins(),
                having=self._compile_having(),
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

    def _compile_joins(self):
        sql = ""
        for join in self._joins:
            local_table = join.column1.split(".")[0]
            column1 = join.column1.split(".")[1]
            column2 = join.column2.split(".")[1]
            sql += self.join_string().format(
                foreign_table=self._compile_table(join.foreign_table),
                local_table=self._compile_table(local_table),
                column1=self._compile_column(column1),
                equality=join.equality,
                column2=self._compile_column(column2),
                keyword=self.join_keywords[join.clause],
            )
            sql += " "

        return sql

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
        for update in self._updates:

            if update.update_type == "increment":
                sql_string = self.increment_string()
            elif update.update_type == "decrement":
                sql_string = self.decrement_string()
            else:
                sql_string = self.key_value_string()

            column = update.column
            value = update.value
            if isinstance(column, dict):
                for key, value in column.items():
                    sql += sql_string.format(
                        column=self._compile_column(key),
                        value=value if not qmark else "?",
                    )

                    if qmark:
                        self._bindings += (value,)
            else:
                sql += sql_string.format(
                    column=self._compile_column(column),
                    value=value if not qmark else "?",
                )
                if qmark:
                    self._bindings += (value,)

        return sql

    def _compile_aggregates(self):
        sql = ""
        for aggregates in self._aggregates:
            aggregate, column = aggregates
            aggregate_function = self.aggregate_options.get(aggregate, "")
            if column == "*":
                aggregate_string = self.aggregate_string_without_alias()
            else:
                aggregate_string = self.aggregate_string_with_alias()

            sql += aggregate_string.format(
                aggregate_function=aggregate_function,
                column="*" if column == "*" else self._compile_column(column),
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

    def _compile_table(self, table):
        return self.table_string().format(
            table=table,
            database=self._connection_details.get("database", ""),
            prefix=self._connection_details.get("prefix", ""),
        )

    def _compile_limit(self):
        if not self._limit:
            return ""

        return self.limit_string(offset=self._offset).format(limit=self._limit)

    def _compile_offset(self):
        if not self._offset:
            return ""

        return self.offset_string().format(offset=self._offset, limit=self._limit)

    def _compile_having(self, qmark=False):
        sql = ""
        for having in self._having:
            column = having.column
            equality = having.equality
            value = having.value

            if not equality and not value:
                sql_string = self.having_string()
            else:
                sql_string = self.having_equality_string()

            sql += sql_string.format(
                column=self._compile_column(column),
                equality=equality,
                value=self._compile_value(value),
            )

        return sql

    def _compile_wheres(self, qmark=False, strip_first_where=False):
        sql = ""
        loop_count = 0
        for where in self._wheres:
            column = where.column
            equality = where.equality
            value = where.value
            value_type = where.value_type

            """Need to get a specific keyword here. This keyword either needs to be
            something like WHERE, AND, OR.

            Depending on the loop depends on the placement of the AND
            """
            if loop_count == 0:
                if strip_first_where:
                    keyword = ""
                else:
                    keyword = self.first_where_string()
            elif where.keyword == "or":
                keyword = self.or_where_string()
            else:
                keyword = self.additional_where_string()

            if where.raw:
                """If we have a raw query we just want to use the query supplied
                and don't need to compile anything.
                """
                sql += self.raw_query_string().format(
                    keyword=keyword, query=where.column
                )

                self.add_binding(where.bindings)

                continue

            """The column is an easy compile
            """
            column = self._compile_column(column)

            """Need to find which type of where string it is.
            If it is a WHERE NULL, WHERE EXISTS, WHERE `col` = 'val' etc
            """
            if equality == "BETWEEN":
                sql_string = self.between_string().format(
                    low=self._compile_value(where.low),
                    high=self._compile_value(where.high),
                    column=self._compile_table(where.column),
                    keyword=keyword,
                )
            elif value is None:
                sql_string = self.where_null_string()
            elif value is True:
                sql_string = self.where_not_null_string()
            elif equality == "EXISTS":
                sql_string = self.where_exists_string()
            else:
                sql_string = self.where_string()

            """If the value should actually be a sub query then we need to wrap it in a query here
            """
            if isinstance(value, SubGroupExpression):
                query_value = self.subquery_string().format(
                    query=value.builder.get_grammar()._compile_wheres(
                        strip_first_where=True
                    )
                )
                sql_string = self.where_group_string()
            elif isinstance(value, SubSelectExpression):
                query_value = self.subquery_string().format(
                    query=value.builder.to_sql()
                )
            elif isinstance(value, list):
                query_value = "("
                for val in value:
                    if qmark:
                        query_value += "'?', "
                        self.add_binding(val)
                    else:
                        query_value += self.value_string().format(
                            value=val, seperator=","
                        )
                query_value = query_value.rstrip(",").rstrip(", ") + ")"
            elif qmark:
                query_value = "'?'"
                self.add_binding(value)
            elif value_type == "value":
                query_value = self.value_string().format(value=value, seperator="")
            elif value_type == "column":
                query_value = self.column_string().format(column=value, seperator="")
            elif value_type == "having":
                query_value = self.column_string().format(column=value, seperator="")
            else:
                query_value = ""

            sql += sql_string.format(
                keyword=keyword, column=column, equality=equality, value=query_value,
            )

            loop_count += 1

        return sql

    def add_binding(self, binding):
        self._bindings += (binding,)

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

        return re.sub(" +", " ", self._sql.strip())

    def to_qmark(self):
        """Cleans up the SQL string and returns the SQL

        Returns:
            string
        """
        return re.sub(" +", " ", self._sql.strip())

    def _compile_columns(self, seperator=""):
        sql = ""

        if self._columns != "*":
            for column in self._columns:
                if isinstance(column, SelectExpression):
                    if column.raw:
                        sql += column.column
                        continue

                    column = column.column
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
        return self.column_string().format(
            column=column, seperator=seperator, table=self.table
        )

    def _compile_value(self, value, seperator=""):
        return self.value_string().format(value=value, seperator=seperator)

    def drop_table(self, table):
        self._sql = self.drop_table_string().format(table=self._compile_column(table))
        return self

    def drop_table_if_exists(self, table):
        self._sql = self.drop_table_if_exists_string().format(
            table=self._compile_column(table)
        )
        return self
