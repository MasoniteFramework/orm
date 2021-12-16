from .BaseGrammar import BaseGrammar


class MySQLGrammar(BaseGrammar):
    """MySQL grammar class."""

    aggregate_options = {
        "SUM": "SUM",
        "MAX": "MAX",
        "MIN": "MIN",
        "AVG": "AVG",
        "COUNT": "COUNT",
        "AVG": "AVG",
    }

    join_keywords = {
        "inner": "INNER JOIN",
        "join": "INNER JOIN",
        "outer": "OUTER JOIN",
        "left": "LEFT JOIN",
        "right": "RIGHT JOIN",
        "left_inner": "LEFT INNER JOIN",
        "right_inner": "RIGHT INNER JOIN",
    }

    """Column strings are formats for how columns and key values should be formatted
    on specific queries. These can be different depending on the type of query.

    For example for Postgres, You can specify columns as "users"."name":

        SELECT "users"."name" from "users"

    But on updates we can only specify the column name and cannot have the table prefixed:

        UPDATE "users" SET "name" = "value"

    This dictionary allows you to modify the format depending on the type
    of query we are generating. For most databases these will be the same
    but this allows you to modify formats depending on the database.
    """

    column_strings = {
        "select": "{table}.`{column}`{alias}{separator}",
        "select_all": "{table}.*{separator}",
        "insert": "{table}.`{column}`{separator}",
        "update": "{table}.`{column}`{separator}",
        "delete": "{table}.`{column}`{separator}",
    }

    locks = {"share": "LOCK IN SHARE MODE", "update": "FOR UPDATE"}

    def select_format(self):
        return "SELECT {columns} FROM {table} {joins} {wheres} {group_by} {order_by} {limit} {offset} {having} {lock}"

    def select_no_table(self):
        return "SELECT {columns} {lock}"

    def update_format(self):
        return "UPDATE {table} SET {key_equals} {wheres}"

    def insert_format(self):
        return "INSERT INTO {table} ({columns}) VALUES ({values})"

    def bulk_insert_format(self):
        return "INSERT INTO {table} ({columns}) VALUES {values}"

    def delete_format(self):
        return "DELETE FROM {table} {wheres}"

    def aggregate_string_with_alias(self):
        return "{aggregate_function}({column}) AS {alias}"

    def aggregate_string_without_alias(self):
        return "{aggregate_function}({column})"

    def subquery_string(self):
        return "({query})"

    def raw_query_string(self):
        return "{keyword} {query}"

    def where_group_string(self):
        return "{keyword} {value}"

    def between_string(self):
        return "{keyword} {column} BETWEEN {low} AND {high}"

    def not_between_string(self):
        return "{keyword} {column} NOT BETWEEN {low} AND {high}"

    def where_exists_string(self):
        return "{keyword} EXISTS {value}"

    def where_not_exists_string(self):
        return "{keyword} NOT EXISTS {value}"

    def where_like_string(self):
        return "{keyword} {column} LIKE {value}"

    def where_not_like_string(self):
        return "{keyword} {column} NOT LIKE {value}"

    def get_true_column_string(self):
        return "{keyword} {column} = '1'"

    def get_false_column_string(self):
        return "{keyword} {column} = '0'"

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
                self.table_string().format(table=t) for t in table.split(".")
            )
        if table.raw:
            return table.name
        return ".".join(
            self.table_string().format(table=t) for t in table.name.split(".")
        )

    def subquery_alias_string(self):
        return "AS {alias}"

    def key_value_string(self):
        return "{column} = '{value}'{separator}"

    def column_value_string(self):
        return "{column} = {value}{separator}"

    def increment_string(self):
        return "{column} = {column} + '{value}'"

    def decrement_string(self):
        return "{column} = {column} - '{value}'"

    def create_column_string(self):
        return "{column} {data_type}{length}{nullable}{default_value}, "

    def column_exists_string(self):
        return "SHOW COLUMNS FROM {table} LIKE {value}"

    def table_exists_string(self):
        return "SELECT * from information_schema.tables where table_name='{clean_table}' AND table_schema = '{database}'"

    def create_column_length(self, column_type):
        return "({length})"

    def table_string(self):
        return "`{table}`"

    def order_by_format(self):
        return "{column} {direction}"

    def order_by_string(self):
        return "ORDER BY {order_columns}"

    def column_string(self):
        return "`{column}`{separator}"

    def value_string(self):
        return "'{value}'{separator}"

    def join_string(self):
        return "{keyword} {foreign_table}{alias} {on}"

    def limit_string(self, offset=False):
        return "LIMIT {limit}"

    def offset_string(self):
        return "OFFSET {offset}"

    def first_where_string(self):
        return "WHERE"

    def additional_where_string(self):
        return "AND"

    def or_where_string(self):
        return "OR"

    def where_in_string(self):
        return "WHERE IN ({values})"

    def value_equal_string(self):
        return "{keyword} {value1} = {value2}"

    def where_string(self):
        return " {keyword} {column} {equality} {value}"

    def having_string(self):
        return "HAVING {column}"

    def having_equality_string(self):
        return "HAVING {column} {equality} {value}"

    def where_null_string(self):
        return " {keyword} {column} IS NULL"

    def where_not_null_string(self):
        return " {keyword} {column} IS NOT NULL"

    def enable_foreign_key_constraints(self):
        return "SET FOREIGN_KEY_CHECKS=1"

    def disable_foreign_key_constraints(self):
        return "SET FOREIGN_KEY_CHECKS=0"

    def truncate_table(self, table, foreign_keys=False):
        """Specifies a truncate table expression.

        Arguments;
            table {string} -- The name of the table to truncate.

        Returns:
            self
        """
        if not foreign_keys:
            return f"TRUNCATE TABLE {self.wrap_table(table)}"

        return [
            self.disable_foreign_key_constraints(),
            f"TRUNCATE TABLE {self.wrap_table(table)}",
            self.enable_foreign_key_constraints(),
        ]
