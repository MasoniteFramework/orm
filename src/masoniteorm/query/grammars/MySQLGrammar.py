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
        "outer": "OUTER JOIN",
        "left": "LEFT JOIN",
        "right": "RIGHT JOIN",
        "left_inner": "LEFT INNER JOIN",
        "right_inner": "RIGHT INNER JOIN",
    }

    type_map = {
        "string": "VARCHAR",
        "char": "CHAR",
        "integer": "INT",
        "big_integer": "BIGINT",
        "tiny_integer": "TINYINT",
        "big_increments": "BIGINT AUTO_INCREMENT",
        "small_integer": "SMALLINT",
        "medium_integer": "MEDIUMINT",
        "increments": "INT UNSIGNED AUTO_INCREMENT PRIMARY KEY",
        "binary": "LONGBLOB",
        "boolean": "BOOLEAN",
        "decimal": "DECIMAL",
        "double": "DOUBLE",
        "enum": "ENUM",
        "text": "TEXT",
        "float": "FLOAT",
        "geometry": "GEOMETRY",
        "json": "JSON",
        "jsonb": "LONGBLOB",
        "long_text": "LONGTEXT",
        "point": "POINT",
        "time": "TIME",
        "timestamp": "TIMESTAMP",
        "date": "DATE",
        "year": "YEAR",
        "datetime": "DATETIME",
        "tiny_increments": "TINYINT AUTO_INCREMENT",
        "unsigned": "INT UNSIGNED",
        "unsigned_integer": "INT UNSIGNED",
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
        "select": "`{table}`.`{column}`{separator}",
        "insert": "`{table}`.`{column}`{separator}",
        "update": "`{table}`.`{column}`{separator}",
        "delete": "`{table}`.`{column}`{separator}",
    }

    def select_format(self):
        return "SELECT {columns} FROM {table} {joins} {wheres} {group_by}{order_by} {limit} {offset} {having}"

    def update_format(self):
        return "UPDATE {table} SET {key_equals} {wheres}"

    def insert_format(self):
        return "INSERT INTO {table} ({columns}) VALUES ({values})"

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

    def subquery_alias_string(self):
        return "AS {alias}"

    def key_value_string(self):
        return "{column} = '{value}'{separator}"

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

    def order_by_string(self):
        return "ORDER BY {column} {direction}"

    def column_string(self):
        return "`{column}`{separator}"

    def value_string(self):
        return "'{value}'{separator}"

    def join_string(self):
        return "{keyword} {foreign_table} ON {column1} {equality} {column2}"

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
        return "{keyword} {column} IS NULL"

    def where_not_null_string(self):
        return " {keyword} {column} IS NOT NULL"
