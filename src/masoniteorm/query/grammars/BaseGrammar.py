import re

from ...expressions.expressions import (
    SubGroupExpression,
    SubSelectExpression,
    SelectExpression,
    BetweenExpression,
    JoinClause,
    OnClause,
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
        updates=None,
        aggregates=(),
        order_by=(),
        group_by=(),
        joins=(),
        lock=False,
        having=(),
        connection_details=None,
    ):
        self._columns = columns
        self.table = table
        self.database = database
        self._wheres = wheres
        self._limit = limit
        self._offset = offset
        self._updates = updates or {}
        self._aggregates = aggregates
        self._order_by = order_by
        self._group_by = group_by
        self._joins = joins
        self._having = having
        self.lock = lock
        self._connection_details = connection_details or {}
        self._column = None

        self._bindings = []

        self._sql = ""

        self._sql_qmark = ""
        self._action = "select"
        self.queries = []

    def compile(self, action, qmark=False):
        self._action = action
        return getattr(self, "_compile_" + action)(qmark=qmark)

    def _compile_select(self, qmark=False):
        """Compile a select query statement.

        Keyword Arguments:
            qmark {bool} -- [description] (default: {False})

        Returns:
            [type] -- [description]
        """
        if not self.table:
            self._sql = (
                self.select_no_table()
                .format(
                    columns=self.process_columns(separator=", ", qmark=qmark),
                    table=self.process_table(self.table),
                    joins=self.process_joins(qmark=qmark),
                    wheres=self.process_wheres(qmark=qmark),
                    limit=self.process_limit(),
                    offset=self.process_offset(),
                    aggregates=self.process_aggregates(),
                    order_by=self.process_order_by(),
                    group_by=self.process_group_by(),
                    having=self.process_having(),
                    lock=self.process_locks(),
                )
                .strip()
            )
        else:
            self._sql = (
                self.select_format()
                .format(
                    columns=self.process_columns(separator=", ", qmark=qmark),
                    table=self.process_table(self.table),
                    joins=self.process_joins(qmark=qmark),
                    wheres=self.process_wheres(qmark=qmark),
                    limit=self.process_limit(),
                    offset=self.process_offset(),
                    aggregates=self.process_aggregates(),
                    order_by=self.process_order_by(),
                    group_by=self.process_group_by(),
                    having=self.process_having(),
                    lock=self.process_locks(),
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
            table=self.process_table(self.table),
            wheres=self.process_wheres(qmark=qmark),
        )

        return self

    def _compile_insert(self, qmark=False):
        """Compiles an insert expression.

        Returns:
            self
        """
        self._sql = self.insert_format().format(
            key_equals=self._compile_key_value_equals(qmark=qmark),
            table=self.process_table(self.table),
            columns=self.process_columns(separator=", ", action="insert", qmark=qmark),
            values=self.process_values(separator=", ", qmark=qmark),
        )

        return self

    def _compile_bulk_create(self, qmark=False):
        """Compiles an insert expression.

        Returns:
            self
        """
        all_values = [list(x.values()) for x in self._columns]

        self._sql = self.bulk_insert_format().format(
            key_equals=self._compile_key_value_equals(qmark=qmark),
            table=self.process_table(self.table),
            columns=self.columnize_bulk_columns(list(self._columns[0].keys())),
            values=self.columnize_bulk_values(all_values, qmark=qmark),
        )
        return self

    def columnize_bulk_columns(self, columns=[]):
        return ", ".join(
            self.column_string().format(column=x, separator="") for x in columns
        ).rstrip(",")

    def columnize_bulk_values(self, columns=[], qmark=False):
        sql = ""
        for x in columns:
            inner = ""
            if isinstance(x, list):
                for y in x:
                    if qmark:
                        self.add_binding(y)
                    inner += (
                        "'?', "
                        if qmark
                        else self.value_string().format(value=y, separator=", ")
                    )

                inner = inner.rstrip(", ")
                sql += self.process_value_string().format(value=inner, separator=", ")
            else:
                if qmark:
                    self.add_binding(x)
                sql += (
                    "'?', "
                    if qmark
                    else self.process_value_string().format(
                        value="?" if qmark else x, separator=", "
                    )
                )

        return sql.rstrip(", ")

    def process_value_string(self):
        return "({value}){separator}"

    def _compile_delete(self, qmark=False):
        """Compiles a delete expression.

        Returns:
            self
        """
        self._sql = self.delete_format().format(
            key_equals=self._compile_key_value_equals(qmark=qmark),
            table=self.process_table(self.table),
            wheres=self.process_wheres(qmark=qmark),
        )

        return self

    # TODO: Columnize?
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
                column_string += self.process_column(col) + ", "
            return column_string.rstrip(", ")

        return self.process_column(columns)

    def process_joins(self, qmark=False):
        """Compiles a join expression.

        Returns:
            self
        """
        sql = ""
        for join in self._joins:
            if isinstance(join, JoinClause):
                on_string = ""
                for clause_idx, clause in enumerate(join.get_on_clauses()):
                    keyword = clause.operator.upper() if clause_idx else "ON"

                    if isinstance(clause, OnClause):
                        on_string += f"{keyword} {self._table_column_string(clause.column1)} {clause.equality} {self._table_column_string(clause.column2)} "
                    else:
                        if clause.value_type == "NULL":
                            sql_string = self.where_null_string()
                            on_string += sql_string.format(
                                keyword=keyword,
                                column=self.process_column(clause.column),
                            )
                        elif clause.value_type == "NOT NULL":
                            sql_string = self.where_not_null_string()
                            on_string += sql_string.format(
                                keyword=keyword,
                                column=self.process_column(clause.column),
                            )
                        else:
                            if qmark:
                                value = "'?'"
                                self.add_binding(clause.value)
                            else:
                                value = self._compile_value(clause.value)
                            on_string += f"{keyword} {self._table_column_string(clause.column)} {clause.equality} {value} "

                sql += self.join_string().format(
                    foreign_table=self.process_table(join.table),
                    alias=f" AS {self.process_table(join.alias)}" if join.alias else "",
                    on=on_string,
                    keyword=self.join_keywords[join.clause],
                )
                sql += " "

        return sql

    # TODO: Clean
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

                    if hasattr(value, "expression"):
                        sql += self.column_value_string().format(
                            column=self._table_column_string(key),
                            value=value.expression,
                            separator=", ",
                        )
                    else:
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
                    separator=", ",
                )
                if qmark:
                    self._bindings += (value,)

        sql = sql.rstrip(", ")
        return sql

    def process_aggregates(self):
        """Compiles aggregates to be used in a query expression.

        Returns:
            self
        """
        sql = ""
        for aggregates in self._aggregates:
            aggregate = aggregates.aggregate
            column = aggregates.column
            aggregate_function = self.aggregate_options.get(aggregate, "")
            if not aggregates.alias and column == "*":
                aggregate_string = self.aggregate_string_without_alias()
            else:
                aggregate_string = self.aggregate_string_with_alias()

            sql += (
                aggregate_string.format(
                    aggregate_function=aggregate_function,
                    column="*" if column == "*" else self._table_column_string(column),
                    alias=self.process_alias(aggregates.alias or column),
                )
                + ", "
            )

        return sql

    def process_order_by(self):
        """Compiles an order by for a query expression.

        Returns:
            self
        """
        sql = ""
        if self._order_by:
            order_crit = ""
            for order_bys in self._order_by:
                if order_bys.raw:
                    order_crit += order_bys.column
                    if not isinstance(order_bys.bindings, (list, tuple)):
                        raise ValueError(
                            f"Bindings must be tuple or list. Received {type(order_bys.bindings)}"
                        )

                    if order_bys.bindings:
                        self.add_binding(*order_bys.bindings)

                    continue

                if len(order_crit):
                    order_crit += ", "
                column = order_bys.column
                direction = order_bys.direction
                if "." in column:
                    column_string = self._table_column_string(column)
                else:
                    column_string = self.column_string().format(
                        column=column, separator=""
                    )
                order_crit += self.order_by_format().format(
                    column=column_string, direction=direction.upper()
                )

            sql += self.order_by_string().format(order_columns=order_crit)
        return sql

    def process_group_by(self):
        """Compiles a group by for a query expression.

        Returns:
            self
        """
        sql = ""
        columns = []
        for group_by in self._group_by:
            if group_by.raw:
                if group_by.bindings:
                    self.add_binding(*group_by.bindings)

                sql += "GROUP BY " + group_by.column
                return sql

            else:
                columns.append(self._table_column_string(group_by.column))

        if columns:
            sql += " GROUP BY {column}".format(column=", ".join(columns))

        return sql

    def process_alias(self, column):
        """Compiles an alias for a column.

        Arguments:
            column {string} -- The name of the column.

        Returns:
            self
        """
        return column

    def process_table(self, table):
        """Compiles a given table name.

        Arguments:
            table {string} -- The table name to compile.

        Returns:
            self
        """
        if not table:
            return ""

        if isinstance(table, str):
            return ".".join(
                self.table_string().format(
                    table=t,
                    database=self._connection_details.get("database", ""),
                    prefix=self._connection_details.get("prefix", ""),
                )
                for t in table.split(".")
            )

        if table.raw:
            return table.name

        return ".".join(
            self.table_string().format(
                table=t,
                database=self._connection_details.get("database", ""),
                prefix=self._connection_details.get("prefix", ""),
            )
            for t in table.name.split(".")
        )

    def process_limit(self):
        """Compiles the limit expression.

        Returns:
            self
        """
        if not self._limit:
            return ""

        return self.limit_string(offset=self._offset).format(limit=self._limit)

    def process_offset(self):
        """Compiles the offset expression.

        Returns:
            self
        """
        if not self._offset:
            return ""

        return self.offset_string().format(offset=self._offset, limit=self._limit or 1)

    def process_locks(self):
        return self.locks.get(self.lock, "")

    def process_having(self, qmark=False):
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

    def process_wheres(self, qmark=False, strip_first_where=False):
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
                    keyword = " " + self.first_where_string()
            elif hasattr(where, "keyword") and where.keyword == "or":
                keyword = " " + self.or_where_string()
            else:
                keyword = " " + self.additional_where_string()

            if where.raw:
                """If we have a raw query we just want to use the query supplied
                and don't need to compile anything.
                """
                sql += self.raw_query_string().format(
                    keyword=keyword, query=where.column
                )

                if not isinstance(where.bindings, (list, tuple)):
                    raise ValueError(
                        f"Bindings must be tuple or list. Received {type(where.bindings)}"
                    )

                if where.bindings:
                    self.add_binding(*where.bindings)

                loop_count += 1

                continue

            """The column is an easy compile
            """
            column = self._table_column_string(column)

            """Need to find which type of where string it is.
            If it is a WHERE NULL, WHERE EXISTS, WHERE `col` = 'val' etc
            """
            if equality == "BETWEEN":
                low = where.low
                high = where.high
                if qmark:
                    self.add_binding(low)
                    self.add_binding(high)
                    low = "?"
                    high = "?"

                sql_string = self.between_string().format(
                    low=self._compile_value(low),
                    high=self._compile_value(high),
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
            elif equality == "NOT EXISTS":
                sql_string = self.where_not_exists_string()
            elif equality.upper() == "LIKE":
                sql_string = self.where_like_string()
            elif equality.upper() == "NOT LIKE":
                sql_string = self.where_not_like_string()
            else:
                sql_string = self.where_string()

            """If the value should actually be a sub query then we need to wrap it in a query here
            """
            if isinstance(value, SubGroupExpression):
                grammar = value.builder.get_grammar()
                query_value = (
                    self.subquery_string()
                    .format(
                        query=grammar.process_wheres(
                            qmark=qmark, strip_first_where=True
                        )
                    )
                    .replace("(  ", "(")
                )
                if grammar._bindings:
                    self.add_binding(grammar._bindings)
                sql_string = self.where_group_string()
            elif isinstance(value, SubSelectExpression):
                if qmark:
                    query_from_builder = value.builder.to_qmark()
                    if value.builder._bindings:
                        self.add_binding(value.builder._bindings)
                else:
                    query_from_builder = value.builder.to_sql()
                query_value = self.subquery_string().format(query=query_from_builder)
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
            elif value is True and value_type != "NOT NULL":
                sql_string = self.get_true_column_string()
                query_value = 1
            elif value is False and value_type != "NOT NULL":
                sql_string = self.get_false_column_string()
                query_value = 0
            elif qmark and value_type != "column":
                query_value = "'?'"
                if (
                    value is not True
                    and value_type != "value_equals"
                    and value_type != "NULL"
                    and value_type != "BETWEEN"
                ):
                    self.add_binding(value)
            elif value_type == "value":
                if qmark:
                    query_value = "'?'"
                else:
                    query_value = self.value_string().format(value=value, separator="")

                self.add_binding(value)
            elif value_type == "column":
                query_value = self._table_column_string(column=value, separator="")
            elif value_type == "having":
                query_value = self._table_column_string(column=value, separator="")
            else:
                query_value = ""

            sql += sql_string.format(
                keyword=keyword, column=column, equality=equality, value=query_value
            )

            loop_count += 1

        return sql

    def get_true_column_string(self):
        return "{keyword} {column} = '1'"

    def get_false_column_string(self):
        return "{keyword} {column} = '0'"

    def add_binding(self, binding):
        """Adds a binding to the bindings tuple.

        Arguments:
            binding {string} -- A value to bind.
        """
        if isinstance(binding, list):
            self._bindings += binding
        else:
            self._bindings.append(binding)

    def column_exists(self, column):
        """Check if a column exists

        Arguments:
            column {string} -- The name of the column to check for existence.

        Returns:
            self
        """
        self._column = column
        self._sql = self.process_exists()
        return self

    def table_exists(self):
        """Checks if a table exists.

        Returns:
            self
        """
        self._sql = self.table_exists_string().format(
            table=self.process_table(self.table),
            database=self.database,
            clean_table=self.table,
        )
        return self

    def wrap_table(self, table_name):
        return self.table_string().format(table=table_name)

    def process_exists(self):
        """Specifies the column exists expression.

        Returns:
            self
        """
        return self.column_exists_string().format(
            table=self.process_table(self.table),
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

    # TODO: Inspect this can't just be used by another method. seems duplicative
    def process_columns(self, separator="", action="select", qmark=False):
        """Specifies the columns in a selection expression.

        Keyword Arguments:
            separator {str} -- The separator used between columns (default: {""})

        Returns:
            self
        """
        sql = ""
        for column in self._columns:
            alias = None
            if isinstance(column, SelectExpression):
                alias = column.alias
                if column.raw:
                    sql += column.column + ", "
                    continue

                column = column.column

            if isinstance(column, SubGroupExpression):
                if qmark:
                    builder_sql = column.builder.to_qmark()
                    if column.builder._bindings:
                        self.add_binding(*column.builder._bindings)
                else:
                    builder_sql = column.builder.to_sql()
                sql += f"({builder_sql}) AS {column.alias}, "
                continue

            sql += self._table_column_string(column, alias=alias, separator=separator)

        if self._aggregates:
            sql += self.process_aggregates()

        if sql == "":
            return "*"

        return sql.rstrip(",").rstrip(", ")

    # TODO: Duplicative?
    def process_values(self, separator="", qmark=False):
        """Compiles column values for insert expressions.

        Keyword Arguments:
            separator {str} -- The separator used between columns (default: {""})

        Returns:
            self
        """
        sql = ""
        if self._columns == "*":
            return self._columns
        elif isinstance(self._columns, list):
            for c in self._columns:
                for column, value in dict(c).items():
                    if qmark:
                        self.add_binding(value)
                        sql += f"'?'{separator}".strip()
                    else:
                        sql += self._compile_value(value, separator=separator)
        else:
            for column, value in dict(self._columns).items():
                if qmark:
                    self.add_binding(value)
                    sql += f"'?'{separator}".strip()
                else:
                    sql += self._compile_value(value, separator=separator)

        if not qmark:
            return sql[:-2]

        return sql.rstrip(separator.strip())

    def process_column(self, column, separator=""):
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

    def _table_column_string(self, column, alias=None, separator=""):
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

        if column == "*":
            return self.column_strings.get("select_all").format(
                column=column,
                separator=separator,
                table=self.process_table(table or self.table),
            )

        if alias:
            alias_string = self.subquery_alias_string().format(alias=alias)
        return self.column_strings.get(self._action).format(
            column=column,
            separator=separator,
            alias=" " + alias_string if alias else "",
            table=self.process_table(table or self.table),
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
        self._sql = self.drop_table_string().format(table=self.process_column(table))
        return self

    def drop_table_if_exists(self, table):
        """Specifies a drop table if exists expression.

        Arguments:
            table {string} -- The name of the table to drop.

        Returns:
            self
        """
        self._sql = self.drop_table_if_exists_string().format(
            table=self.process_column(table)
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
            current_table_name=self.process_column(current_table_name),
            new_table_name=self.process_column(new_table_name),
        )
        return self

    def truncate_table(self, table, foreign_keys=False):
        """Specifies a truncate table expression.

        Arguments;
            table {string} -- The name of the table to truncate.

        Returns:
            self
        """
        raise NotImplementedError(
            f"'{self.__class__.__name__}' does not support truncating"
        )
