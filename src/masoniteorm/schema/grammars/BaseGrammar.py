import re

from ...expressions.expressions import (
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
        database=None,
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
        constraints=(),
        foreign_keys=(),
        connection_details={},
    ):
        self._columns = columns
        self.table = table
        self.database = database
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
        self._constraints = constraints
        self._foreign_keys = foreign_keys
        self._connection_details = connection_details
        self._column = None

        self._bindings = ()

        self._sql = ""

        self._sql_qmark = ""
        self._action = "select"
        self.queries = []

    def compile(self, action):
        self._action = action
        return getattr(self, "_compile_" + action)()

    def _compile_create(self):
        """Compiles a query for creating new table schemas.

        Returns:
            self
        """
        self._sql = self.create_format().format(
            table=self._compile_table(self.table),
            columns=self._compile_create_columns(),
            constraints=self._compile_create_constraints().rstrip(" "),
            foreign_keys=self._compile_foreign_keys().rstrip(" "),
        )
        return self

    def _compile_alter(self):
        """Compiles a query for altering table schemas.

        Returns:
            self
        """
        self._sql = self.alter_format().format(
            table=self._compile_table(self.table),
            columns=self._compile_alter_columns(),
            constraints=self._compile_alter_constraints(),
            foreign_keys=self._compile_alter_foreign_keys(),
        )

        self._sql = self._sql.rstrip(", ")

        return self

    def _compile_alter_columns(self):
        """Compiles the columns for alter statements.

        Returns:
            self
        """
        sql = ""
        for column in self._creates:
            nullable = ""
            if column.is_null and column._action == "modify":
                nullable = " NULL"
            elif not column.is_null:
                nullable = " NOT NULL"

            sql += getattr(self, "{}_column_string".format(column._action))().format(
                column=self._compile_column(column.column_name),
                old_column=self._compile_column(column.old_column),
                data_type=self.type_map.get(column.column_type, ""),
                length=self.create_column_length(column.column_type).format(
                    length=column.length
                )
                if column.length
                else "",
                nullable=nullable,
                separator=",",
                after=self.after_column_string().format(
                    after=self._compile_column(column.after_column)
                )
                if column.after_column
                else "",
            )

        # Fix any inconsistencies
        sql = sql.replace(" ,", ",")

        return sql

    def _compile_foreign_keys(self):
        """Compiles the foreign keys for creation statements.

        Returns:
            self
        """
        sql = ", "
        for foreign_key in self._foreign_keys:
            sql += self.foreign_key_string().format(
                column=self._compile_column(foreign_key.column_name),
                foreign_table=self._compile_table(foreign_key.foreign_table),
                foreign_column=self._compile_column(foreign_key.foreign_column),
                index_name=foreign_key.index_name,
                separator=", ",
            )

        return sql.rstrip(", ")

    def _compile_alter_foreign_keys(self):
        """Compiles the foreign keys for alter statements.

        Returns:
            self
        """
        sql = " "
        for foreign_key in self._foreign_keys:
            if foreign_key._on_delete:
                action = self.on_delete_mapping[foreign_key._on_delete]
            elif foreign_key._on_update:
                action = self.on_update_mapping[foreign_key._on_update]
            else:
                action = ""

            sql += self.alter_foreign_key_string().format(
                column=self._compile_column(foreign_key.column_name),
                foreign_table=self._compile_table(foreign_key.foreign_table),
                foreign_column=self._compile_column(foreign_key.foreign_column),
                index_name=foreign_key.index_name,
                action=action,
                separator=", ",
            )

        return sql.rstrip(", ")

    def _compile_create_columns(self):
        """Compiles columns for create statements.

        Returns:
            self
        """
        sql = ""
        for column in self._creates:
            default = column.default
            # Get the default value. Can fetch from premapped defaults. should default to the value on the column class.
            if column.default is not None and column.default in self.premapped_defaults:
                default = self.premapped_defaults.get(column.default)
            elif default is not None:
                default = self.default_string().format(default=column.default)
            else:
                default = ""

            length_string = (
                self.create_column_length(column.column_type).format(
                    length=column.length
                )
                if column.length
                else ""
            )

            if hasattr(self, f"_type_{column.column_type}"):
                sql += getattr(self, f"_type_{column.column_type}")(
                    column, length_string, default
                )
                continue

            attributes = {
                "column": self._compile_column(column.column_name),
                "data_type": self.type_map.get(column.column_type),
                "length": length_string,
                "nullable": " ",
                "default_value": default,
            }

            if not column.is_null:
                attributes.update({"nullable": " NOT NULL"})
            else:
                attributes.update({"nullable": " NULL"})
            sql += self.create_column_string().format(**attributes)

        if not self._constraints:
            sql = sql.rstrip(", ")
        return sql.strip()

    def _get_multiple_columns(self, columns):
        """Compiles a string or a list of strings into the grammars column syntax.

        Arguments:
            columns {string|list} -- A column or list of columns

        Returns:
            self
        """
        if isinstance(columns, list):
            column_string = ""
            for col in columns:
                column_string += self._compile_column(col) + ", "
            return column_string.rstrip(", ")

        return self._compile_column(columns)

    def _compile_create_constraint_as_query(self, column):
        """Compiles constraints for creation schema.

        Returns:
            self
        """
        if not self.options["can_compile_multiple_index"] and isinstance(
            column.column_name, list
        ):
            for index_column in column.column_name:
                query = getattr(
                    self, "{}_constraint_string".format(column.constraint_type)
                )().format(
                    column=self._compile_column(index_column),
                    clean_column=index_column,
                    index_name=column.index_name,
                    table=self._compile_table(self.table),
                    clean_table=self.table,
                    separator="",
                )
                self.queries.append(query.rstrip(" "))
        else:

            query = getattr(
                self, "{}_constraint_string".format(column.constraint_type)
            )().format(
                column=self._get_multiple_columns(column.column_name),
                clean_column=column.column_name,
                index_name=column.index_name,
                table=self._compile_table(self.table),
                clean_table=self.table,
                separator="",
            )
            self.queries.append(query.rstrip(" "))

    def _compile_create_constraints(self):
        """Compiles constraints for creation schema.

        Returns:
            self
        """
        sql = " "

        for column in self._constraints:
            if self.options.get(
                "create_constraints_as_separate_queries"
            ) and column.constraint_type in self.options.get(
                "second_query_constraints"
            ):
                self._compile_create_constraint_as_query(column)
                continue
            sql += getattr(
                self, "{}_constraint_string".format(column.constraint_type)
            )().format(
                column=self._get_multiple_columns(column.column_name),
                clean_column=column.column_name,
                index_name=column.index_name,
                table=self._compile_table(self.table),
                clean_table=self.table,
                separator=", ",
            )

        return sql.rstrip(", ")

    def _compile_alter_constraint_as_query(self, column, action):
        """Compiles constraints for creation schema.

        Returns:
            self
        """
        if not self.options["can_compile_multiple_index"] and isinstance(
            column.column_name, list
        ):
            for index_column in column.column_name:
                query = getattr(
                    self, "{}_{}_column_string".format(action, column.constraint_type)
                )().format(
                    column=self._compile_column(index_column),
                    clean_column=index_column,
                    index_name=column.index_name,
                    table=self._compile_table(self.table),
                    clean_table=self.table,
                    separator="",
                )
                self.queries.append(query.rstrip(" "))
        else:
            query = getattr(
                self, "{}_{}_column_string".format(action, column.constraint_type)
            )().format(
                column=self._get_multiple_columns(column.column_name),
                clean_column=column.column_name,
                index_name=column.index_name,
                table=self._compile_table(self.table),
                clean_table=self.table,
                separator="",
            )
            self.queries.append(query.rstrip(" "))

    def _compile_alter_constraints(self):
        """Compiles constraints for alter schema.

        Returns:
            self
        """
        sql = " "
        for column in self._constraints:
            if self.options.get(
                "alter_constraints_as_separate_queries"
            ) and column.constraint_type in self.options.get(
                "second_query_constraints"
            ):
                self._compile_alter_constraint_as_query(column, column.action)
                continue
            sql += getattr(
                self,
                "{}_{}_column_string".format(
                    column.action,
                    column.constraint_type,
                ),
            )().format(
                column=self._get_multiple_columns(column.column_name),
                clean_column=column.column_name,
                index_name=column.index_name,
                table=self._compile_table(self.table),
                clean_table=self.table,
                separator=", ",
            )

        return sql.rstrip(", ")

    def _compile_select(self, qmark=False):
        """Compile a select query statement.

        Keyword Arguments:
            qmark {bool} -- [description] (default: {False})

        Returns:
            [type] -- [description]
        """
        self._sql = (
            self.select_format()
            .format(
                columns=self._compile_columns(separator=", "),
                table=self._compile_table(self.table),
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
        """Compiles an update query statement.

        Keyword Arguments:
            qmark {bool} -- Whether the query should use qmark. (default: {False})

        Returns:
            self
        """
        self._sql = self.update_format().format(
            key_equals=self._compile_key_value_equals(qmark=qmark),
            table=self._compile_table(self.table),
            wheres=self._compile_wheres(qmark=qmark),
        )

        return self

    def _compile_joins(self):
        """Compiles a join expression.

        Returns:
            self
        """
        sql = ""
        for join in self._joins:
            local_table = join.column1.split(".")[0]
            column1 = join.column1
            column2 = join.column2
            sql += self.join_string().format(
                foreign_table=self._compile_table(join.foreign_table),
                local_table=self._compile_table(local_table),
                column1=self._table_column_string(column1),
                equality=join.equality,
                column2=self._table_column_string(column2),
                keyword=self.join_keywords[join.clause],
            )
            sql += " "

        return sql

    def _compile_insert(self):
        """Compiles an insert expression.

        Returns:
            self
        """
        self._sql = self.insert_format().format(
            key_equals=self._compile_key_value_equals(),
            table=self._compile_table(self.table),
            columns=self._compile_columns(separator=", ", action="insert"),
            values=self._compile_values(separator=", "),
        )

        return self

    def _compile_delete(self, qmark=False):
        """Compiles a delete expression.

        Returns:
            self
        """
        self._sql = self.delete_format().format(
            key_equals=self._compile_key_value_equals(qmark=qmark),
            table=self._compile_table(self.table),
            wheres=self._compile_wheres(qmark=qmark),
        )

        return self

    def _compile_key_value_equals(self, qmark=False):
        """Compiles key value pairs.

        Keyword Arguments:
            qmark {bool} -- Whether the query should use qmark. (default: {False})

        Returns:
            self
        """
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
                        column=self._table_column_string(key),
                        value=value if not qmark else "?",
                        separator=", ",
                    )

                    if qmark:
                        self._bindings += (value,)
            else:
                sql += sql_string.format(
                    column=self._table_column_string(column),
                    value=value if not qmark else "?",
                    separator=",",
                )
                if qmark:
                    self._bindings += (value,)

            sql = sql.rstrip(", ")

        return sql

    def _compile_aggregates(self):
        """Compiles aggregates to be used in a query expression.

        Returns:
            self
        """
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
                column="*" if column == "*" else self._table_column_string(column),
                alias=self._compile_alias(column),
            )

        return sql

    def _compile_order_by(self):
        """Compiles an order by for a query expression.

        Returns:
            self
        """
        sql = ""
        for order_bys in self._order_by:
            column, direction = order_bys
            sql += self.order_by_string().format(
                column=self._table_column_string(column),
                direction=direction.upper(),
            )

        return sql

    def _compile_group_by(self):
        """Compiles a group by for a query expression.

        Returns:
            self
        """
        sql = ""
        for group_bys in self._group_by:
            column = group_bys
            sql += "GROUP BY {column}".format(column=self._table_column_string(column))

        return sql

    def _compile_alias(self, column):
        """Compiles an alias for a column.

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        return column

    def _compile_table(self, table):
        """Compiles a given table name.

        Arguments:
            table {string} -- The table name to compile.

        Returns:
            self
        """
        return self.table_string().format(
            table=table,
            database=self._connection_details.get("database", ""),
            prefix=self._connection_details.get("prefix", ""),
        )

    def _compile_limit(self):
        """Compiles the limit expression.

        Returns:
            self
        """
        if not self._limit:
            return ""

        return self.limit_string(offset=self._offset).format(limit=self._limit)

    def _compile_offset(self):
        """Compiles the offset expression.

        Returns:
            self
        """
        if not self._offset:
            return ""

        return self.offset_string().format(offset=self._offset, limit=self._limit)

    def _compile_having(self, qmark=False):
        """Compiles having expression.

        Keyword Arguments:
            qmark {bool} -- Whether or not to use Qmark (default: {False})

        Returns:
            self
        """
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
                column=self._table_column_string(column),
                equality=equality,
                value=self._compile_value(value),
            )

        return sql

    def _compile_wheres(self, qmark=False, strip_first_where=False):
        """Compiles the where expression.

        Keyword Arguments:
            qmark {bool} -- Whether or not to use Qmark. (default: {False})
            strip_first_where {bool} -- Whether or not to strip out the first where keyword.
            This is useful when using subselects (default: {False})

        Returns:
            self
        """
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
                keyword = " " + self.additional_where_string()

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
            column = self._table_column_string(column)

            """Need to find which type of where string it is.
            If it is a WHERE NULL, WHERE EXISTS, WHERE `col` = 'val' etc
            """
            if equality == "BETWEEN":
                sql_string = self.between_string().format(
                    low=self._compile_value(where.low),
                    high=self._compile_value(where.high),
                    column=self._table_column_string(where.column),
                    keyword=keyword,
                )
            elif equality == "NOT BETWEEN":
                sql_string = self.not_between_string().format(
                    low=self._compile_value(where.low),
                    high=self._compile_value(where.high),
                    column=self._table_column_string(where.column),
                    keyword=keyword,
                )
            elif value_type == "value_equals":
                sql_string = self.value_equal_string().format(
                    value1=where.column, value2=where.value, keyword=keyword
                )
            elif value_type == "NULL":
                sql_string = self.where_null_string()
            elif value_type == "NOT NULL":
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
                            value=val, separator=","
                        )
                query_value = query_value.rstrip(",").rstrip(", ") + ")"
            elif qmark:
                query_value = "'?'"
                if value is not True and value_type != "value_equals":
                    self.add_binding(value)
            elif value_type == "value":
                query_value = self.value_string().format(value=value, separator="")
            elif value_type == "column":
                query_value = self._table_column_string(column=value, separator="")
            elif value_type == "having":
                query_value = self._table_column_string(column=value, separator="")
            else:
                query_value = ""

            sql += sql_string.format(
                keyword=keyword,
                column=column,
                equality=equality,
                value=query_value,
            )

            loop_count += 1

        return sql

    def add_binding(self, binding):
        """Adds a binding to the bindings tuple.

        Arguments:
            binding {string} -- A value to bind.
        """
        if binding is not None:
            self._bindings += (binding,)

    def column_exists(self, column):
        """Check if a column exists

        Arguments:
            column {string} -- The name of the column to check for existence.

        Returns:
            self
        """
        self._column = column
        self._sql = self._compile_exists()
        return self

    def table_exists(self):
        """Checks if a table exists.

        Returns:
            self
        """
        self._sql = self.table_exists_string().format(
            table=self._compile_table(self.table),
            database=self.database,
            clean_table=self.table,
        )
        return self

    def _compile_exists(self):
        """Specifies the column exists expression.

        Returns:
            self
        """
        return self.column_exists_string().format(
            table=self._compile_table(self.table),
            clean_table=self.table,
            value=self._compile_value(self._column),
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

    def _compile_columns(self, separator="", action="select"):
        """Specifies the columns in a selection expression.

        Keyword Arguments:
            separator {str} -- The separator used between columns (default: {""})

        Returns:
            self
        """
        sql = ""
        for column in self._columns:
            if isinstance(column, SelectExpression):
                if column.raw:
                    sql += column.column
                    continue

                column = column.column
            sql += self._table_column_string(column, separator=separator)

        if self._aggregates:
            sql += self._compile_aggregates()

        if sql == "":
            return "*"

        return sql.rstrip(",").rstrip(", ")

    def _compile_insert_columns(self, separator=""):
        """Specifies the columns in a selection expression.

        Keyword Arguments:
            separator {str} -- The separator used between columns (default: {""})

        Returns:
            self
        """
        sql = ""
        if self._columns != "*":
            for column in self._columns:
                if isinstance(column, SelectExpression):
                    if column.raw:
                        sql += column.column
                        continue

                    column = column.column
                sql += self._table_insert_column_string(column, separator=separator)

        if self._aggregates:
            sql += self._compile_aggregates()

        if sql == "":
            return "*"
        return sql.rstrip(",").rstrip(", ")

    def _compile_values(self, separator=""):
        """Compiles column values for insert expressions.

        Keyword Arguments:
            separator {str} -- The separator used between columns (default: {""})

        Returns:
            self
        """
        sql = ""
        if self._columns == "*":
            return self._columns
        for column, value in dict(self._columns).items():
            sql += self._compile_value(value, separator=separator)

        return sql[:-2]

    def _compile_column(self, column, separator=""):
        """Compiles a column into the column syntax.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            separator {string} -- The separator used between columns (default: {""})

        Returns:
            self
        """
        table = None
        if column and "." in column:
            table, column = column.split(".")
        return self.column_string().format(
            column=column, separator=separator, table=table or self.table
        )

    def _table_column_string(self, column, separator=""):
        """Compiles a column into the column syntax.

        Arguments:
            column {string} -- The name of the column.

        Keyword Arguments:
            separator {string} -- The separator used between columns (default: {""})

        Returns:
            self
        """
        table = None
        if column and "." in column:
            table, column = column.split(".")

        return self.column_strings.get(self._action).format(
            column=column, separator=separator, table=table or self.table
        )

    def _compile_value(self, value, separator=""):
        """Compiles a value using the value syntax.

        Arguments:
            value {string} -- The value to compile.

        Keyword Arguments:
            separator {string} -- The separator used between columns (default: {""})

        Returns:
            self
        """
        return self.value_string().format(value=value, separator=separator)

    def drop_table(self, table):
        """Specifies a drop table expression.

        Arguments:
            table {string} -- The table to drop.

        Returns:
            self
        """
        self._sql = self.drop_table_string().format(table=self._compile_column(table))
        return self

    def drop_table_if_exists(self, table):
        """Specifies a drop table if exists expression.

        Arguments:
            table {string} -- The name of the table to drop.

        Returns:
            self
        """
        self._sql = self.drop_table_if_exists_string().format(
            table=self._compile_column(table)
        )
        return self

    def rename_table(self, current_table_name, new_table_name):
        """Specifies a rename table expression.

        Arguments:
            current_table_name {string} -- The name of the table currently.
            new_table_name {string} -- The name you want to use now for the table.

        Returns:
            self
        """
        self._sql = self.rename_table_string().format(
            current_table_name=self._compile_column(current_table_name),
            new_table_name=self._compile_column(new_table_name),
        )
        return self

    def truncate_table(self, table):
        self._sql = self.truncate_table_string().format(
            table=self._compile_table(table)
        )
        return self
